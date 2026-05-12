"""
Horse Pain Detection — AI Pipeline
Uses YOLO (horse detection) + ViTPose (keypoint extraction) + BiLSTM (classification).
Requires: ultralytics, easy_ViTPose, huggingface_hub, scipy, torch
"""
import os
import numpy as np
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "model", "horse_pain")

MODEL_PATH = os.path.join(MODEL_DIR, "behavior_bilstm.pt")
MEAN_PATH  = os.path.join(MODEL_DIR, "train_mean.npy")
STD_PATH   = os.path.join(MODEL_DIR, "train_std.npy")

# ── Constants (must match training config) ────────────────────────────────────
SEQ_LENGTH   = 64
INPUT_SIZE   = 42
CONF_THRESH  = 0.3
SMOOTH_WIN   = 11
SMOOTH_POLY  = 3
HIDDEN_SIZE  = 64
NUM_LAYERS   = 2
DROPOUT      = 0.4
CLASS_NAMES  = ["normal", "distress"]

JOINT_ANGLE_TRIPLETS = [
    (5,  6,  7),   # LF elbow
    (8,  9,  10),  # RF elbow
    (11, 12, 13),  # LB knee
    (14, 15, 16),  # RB knee
]
SYMMETRY_PAIRS = [
    (11, 14),  # L_Hip vs R_Hip
    (5,  8),   # L_Shoulder vs R_Shoulder
    (7,  10),  # L_F_Paw vs R_F_Paw
    (13, 16),  # L_B_Paw vs R_B_Paw
]

BEHAVIOR_INFO = {
    "normal": {
        "label":   "No Pain",
        "emoji":   "✅",
        "color":   "#16a34a",
        "bg":      "#f0fdf4",
        "border":  "#86efac",
        "desc":    "No significant pain indicators detected in the horse's movement patterns.",
        "advice":  "Horse appears comfortable. Continue regular monitoring and routine veterinary check-ups.",
        "indicators": [
            "Normal gait pattern observed",
            "Regular weight distribution",
            "Relaxed posture and movement",
            "No signs of lameness detected",
        ],
    },
    "distress": {
        "label":   "Pain Detected",
        "emoji":   "⚠️",
        "color":   "#dc2626",
        "bg":      "#fef2f2",
        "border":  "#fca5a5",
        "desc":    "Pain or distress indicators detected in the horse's movement and behavioral patterns.",
        "advice":  "🚨 Consult an equine veterinarian promptly. Restrict strenuous activity until evaluated.",
        "indicators": [
            "Abnormal gait or lameness detected",
            "Irregular weight-bearing patterns",
            "Behavioral stress indicators present",
            "Movement asymmetry observed",
        ],
    },
}

# ── Lazy-loaded models ─────────────────────────────────────────────────────────
_bilstm     = None
_yolo       = None
_pose       = None
_train_mean = None
_train_std  = None
_device     = None


# ── Model definition (must match training exactly) ────────────────────────────
def _build_model():
    import torch
    import torch.nn as nn

    class AttentionPool(nn.Module):
        def __init__(self, hidden_dim):
            super().__init__()
            self.attn = nn.Linear(hidden_dim, 1)

        def forward(self, x):
            w      = torch.softmax(self.attn(x), dim=1)
            pooled = (w * x).sum(dim=1)
            return pooled

    class BehaviorBiLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size    = INPUT_SIZE,
                hidden_size   = HIDDEN_SIZE,
                num_layers    = NUM_LAYERS,
                batch_first   = True,
                bidirectional = True,
                dropout       = DROPOUT if NUM_LAYERS > 1 else 0.0,
            )
            lstm_out     = HIDDEN_SIZE * 2
            self.attn    = AttentionPool(lstm_out)
            self.dropout = nn.Dropout(DROPOUT)
            self.fc      = nn.Sequential(
                nn.Linear(lstm_out, 64),
                nn.ReLU(),
                nn.Dropout(DROPOUT),
                nn.Linear(64, 2),
            )

        def forward(self, x):
            out, _ = self.lstm(x)
            pooled = self.attn(out)
            pooled = self.dropout(pooled)
            return self.fc(pooled)

    return BehaviorBiLSTM()


def _load_models():
    global _bilstm, _yolo, _pose, _train_mean, _train_std, _device
    if _bilstm is not None:
        return

    import torch
    from ultralytics import YOLO
    from huggingface_hub import hf_hub_download

    try:
        from easy_ViTPose import VitInference
    except ImportError as e:
        raise ImportError(
            f"easy_ViTPose not installed. Run: "
            f"pip install git+https://github.com/JunkyByte/easy_ViTPose.git\n"
            f"Original error: {e}"
        )

    _device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _train_mean = np.load(MEAN_PATH).astype(np.float32)
    _train_std  = np.load(STD_PATH).astype(np.float32)

    # Load BiLSTM
    model = _build_model()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=_device, weights_only=False))
    model.to(_device).eval()
    _bilstm = model

    # Download YOLO + ViTPose from HuggingFace (cached after first download)
    vitpose_path = hf_hub_download(
        repo_id="JunkyByte/easy_ViTPose",
        filename="onnx/ap10k/vitpose-b-ap10k.onnx",
    )
    yolo_path = hf_hub_download(
        repo_id="JunkyByte/easy_ViTPose",
        filename="yolov8/yolov8n.pt",
    )
    _yolo = YOLO(yolo_path)
    _pose = VitInference(
        model=vitpose_path,
        yolo=yolo_path,
        dataset="ap10k",
        det_class="horse",
        is_video=False,
    )


# ── Feature extraction (mirrors predict.py exactly) ───────────────────────────
def _interpolate_missing(window):
    T          = window.shape[0]
    out        = window.copy()
    valid_mask = window[:, :, 2] >= CONF_THRESH
    for kp in range(17):
        valid = valid_mask[:, kp]
        if valid.sum() == 0:
            out[:, kp, :2] = 0.0
            continue
        if valid.all():
            continue
        for ch in range(2):
            signal            = out[:, kp, ch].copy()
            signal[~valid]    = np.nan
            valid_idx         = np.where(valid)[0]
            valid_vals        = signal[valid_idx]
            all_idx           = np.arange(T)
            out[:, kp, ch]    = np.interp(all_idx, valid_idx, valid_vals)
    return out, valid_mask


def _smooth_keypoints(window):
    from scipy.signal import savgol_filter
    T      = window.shape[0]
    out    = window.copy()
    win_len = SMOOTH_WIN if T >= SMOOTH_WIN else (T if T % 2 == 1 else T - 1)
    if win_len < 3:
        return out
    poly = min(SMOOTH_POLY, win_len - 1)
    for kp in range(17):
        for ch in range(2):
            out[:, kp, ch] = savgol_filter(out[:, kp, ch], win_len, poly)
    return out


def _normalize_body(window):
    T        = window.shape[0]
    neck     = window[:, 3, :2]
    tail     = window[:, 4, :2]
    body_len = np.linalg.norm(tail - neck, axis=1)
    valid_bl = body_len >= 1.0
    if valid_bl.sum() == 0:
        body_len[:] = 1.0
    else:
        last_valid = None
        for t in range(T):
            if valid_bl[t]:
                last_valid = body_len[t]
            elif last_valid is not None:
                body_len[t] = last_valid
        if not valid_bl[0]:
            first_valid = body_len[np.argmax(valid_bl)]
            for t in range(T):
                if valid_bl[t]:
                    break
                body_len[t] = first_valid
    normed = np.zeros((T, 17, 2))
    for t in range(T):
        for kp in range(17):
            normed[t, kp] = (window[t, kp, :2] - neck[t]) / body_len[t]
    return normed, body_len, int(valid_bl.sum())


def _compute_angle(a, b, c):
    ba      = a - b
    bc      = c - b
    cos_val = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return np.degrees(np.arccos(np.clip(cos_val, -1.0, 1.0)))


def _extract_features(window, valid_mask):
    T                          = window.shape[0]
    interped, _                = _interpolate_missing(window)
    smoothed                   = _smooth_keypoints(interped)
    normed, body_lens, _       = _normalize_body(smoothed)

    coords  = normed.reshape(T, 34)                    # 34 features

    angles  = np.zeros((T, 4))                         # 4 joint angles
    for t in range(T):
        for j, (a_idx, b_idx, c_idx) in enumerate(JOINT_ANGLE_TRIPLETS):
            if valid_mask[t, a_idx] and valid_mask[t, b_idx] and valid_mask[t, c_idx]:
                angles[t, j] = _compute_angle(
                    normed[t, a_idx], normed[t, b_idx], normed[t, c_idx]
                ) / 180.0

    sym = np.zeros((T, 4))                             # 4 symmetry ratios
    for t in range(T):
        for s, (l_idx, r_idx) in enumerate(SYMMETRY_PAIRS):
            sym[t, s] = normed[t, l_idx, 1] - normed[t, r_idx, 1]

    return np.concatenate([coords, angles, sym], axis=1).astype(np.float32)  # (T, 42)


def _process_video(video_path: str) -> np.ndarray:
    import cv2
    cap          = cv2.VideoCapture(video_path)
    W            = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H            = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    all_kps      = []
    last_bbox    = None
    padding      = 50

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        results = _yolo(frame, verbose=False, classes=[17])
        bbox    = None
        if results and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            areas = (boxes.xyxy[:, 2] - boxes.xyxy[:, 0]) * (boxes.xyxy[:, 3] - boxes.xyxy[:, 1])
            best  = areas.argmax().item()
            bbox  = boxes.xyxy[best].cpu().numpy().astype(int)
            last_bbox = bbox
        elif last_bbox is not None:
            bbox = last_bbox

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(W, x2 + padding)
            y2 = min(H, y2 + padding)
            crop = frame[y1:y2, x1:x2]
            try:
                kps_dict = _pose.inference(crop)
                if kps_dict:
                    kps        = list(kps_dict.values())[0].copy()
                    kps[:, 0] += x1
                    kps[:, 1] += y1
                    all_kps.append(kps)
                    continue
            except Exception:
                pass

        all_kps.append(np.zeros((17, 3)))

    cap.release()
    return np.array(all_kps)


# ── Public predict function ────────────────────────────────────────────────────
def predict_horse_pain(video_path: str) -> dict:
    import torch
    import torch.nn.functional as F

    _load_models()

    # Extract keypoints from video
    kps = _process_video(video_path)
    N   = kps.shape[0]
    if N == 0:
        raise ValueError("No valid frames extracted from video.")

    # Center-crop or pad to SEQ_LENGTH
    if N >= SEQ_LENGTH:
        start  = (N - SEQ_LENGTH) // 2
        window = kps[start: start + SEQ_LENGTH]
    else:
        pad    = np.zeros((SEQ_LENGTH - N, 17, 3))
        window = np.concatenate([kps, pad], axis=0)

    # Extract 42 biomechanical features
    _, valid_mask = _interpolate_missing(window)
    features      = _extract_features(window, valid_mask)

    # Normalize
    features = (features - _train_mean) / (_train_std + 1e-8)

    # Run BiLSTM
    tensor = torch.tensor(features).unsqueeze(0).to(_device)
    with torch.no_grad():
        logits = _bilstm(tensor)
        probs  = F.softmax(logits, dim=1)
        conf, pred = probs.max(1)

    class_key  = CLASS_NAMES[pred.item()]
    confidence = conf.item()
    info       = BEHAVIOR_INFO[class_key]

    pain_prob    = float(probs[0, 1].item())
    no_pain_prob = float(probs[0, 0].item())

    return {
        "prediction":            info["label"],
        "confidence":            round(confidence * 100, 1),
        "pain_probability":      round(pain_prob * 100, 1),
        "no_pain_probability":   round(no_pain_prob * 100, 1),
        "emoji":                 info["emoji"],
        "color":                 info["color"],
        "bg":                    info["bg"],
        "border":                info["border"],
        "description":           info["desc"],
        "advice":                info["advice"],
        "behavioral_indicators": info["indicators"],
    }