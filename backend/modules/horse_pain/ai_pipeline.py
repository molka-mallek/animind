"""
Horse Pain Detection — AI Pipeline
BiLSTM model that classifies horse behavior from accelerometer/pose sequences.
Runs in the main backend venv (torch required).
"""
import os
import json
import numpy as np
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "model", "horse_pain")

MODEL_PATH = os.path.join(MODEL_DIR, "behavior_bilstm.pt")
MEAN_PATH  = os.path.join(MODEL_DIR, "train_mean.npy")
STD_PATH   = os.path.join(MODEL_DIR, "train_std.npy")

# ── Behavior knowledge base ────────────────────────────────────────────────
BEHAVIOR_INFO = {
    "No Pain": {
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
    "Pain Detected": {
        "emoji":   "⚠️",
        "color":   "#dc2626",
        "bg":      "#fef2f2",
        "border":  "#fca5a5",
        "desc":    "Pain indicators detected in the horse's movement and behavioral patterns.",
        "advice":  "🚨 Consult an equine veterinarian promptly. Restrict strenuous activity until evaluated.",
        "indicators": [
            "Abnormal gait or lameness detected",
            "Irregular weight-bearing patterns",
            "Behavioral stress indicators present",
            "Movement asymmetry observed",
        ],
    },
}

# ── Lazy-loaded model ──────────────────────────────────────────────────────
_model      = None
_train_mean = None
_train_std  = None
_device     = None
_n_features = None


class _BiLSTMModel:
    """Wrapper that loads the BiLSTM .pt file."""

    def __init__(self, path, device):
        import torch
        import torch.nn as nn

        checkpoint = torch.load(path, map_location=device, weights_only=False)

        # Support both raw state-dict and full checkpoint dicts
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state = checkpoint["model_state_dict"]
        elif isinstance(checkpoint, dict) and any(k.endswith(".weight") or k.endswith(".bias") for k in checkpoint):
            state = checkpoint
        else:
            # Full nn.Module saved with torch.save(model)
            self._net = checkpoint.to(device)
            self._net.eval()
            self._is_full = True
            return

        # ── Infer exact architecture from checkpoint weights ──────────────
        # weight_ih_l0 shape: [4*hidden_size, input_size]
        # weight_hh_l0 shape: [4*hidden_size, hidden_size]
        input_size  = 5   # fallback
        hidden_size = 64  # fallback
        num_layers  = 2   # fallback
        num_classes = 2   # fallback

        for k, v in state.items():
            if k == "lstm.weight_ih_l0":
                # shape [4*H, input_size]
                hidden_size = v.shape[0] // 4
                input_size  = v.shape[1]
            if k == "fc.weight":
                num_classes = v.shape[0]

        # Count layers by checking how many l{n} keys exist
        layer_indices = set()
        for k in state.keys():
            if k.startswith("lstm.weight_ih_l"):
                idx = k.replace("lstm.weight_ih_l", "").replace("_reverse", "")
                if idx.isdigit():
                    layer_indices.add(int(idx))
        if layer_indices:
            num_layers = max(layer_indices) + 1

        class BiLSTM(nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm = nn.LSTM(
                    input_size, hidden_size, num_layers,
                    batch_first=True, bidirectional=True,
                    dropout=0.3 if num_layers > 1 else 0,
                )
                self.fc = nn.Linear(hidden_size * 2, num_classes)

            def forward(self, x):
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])

        net = BiLSTM()
        net.load_state_dict(state, strict=True)
        net.to(device).eval()
        self._net     = net
        self._is_full = False

    def predict(self, x_tensor):
        import torch
        with torch.no_grad():
            logits = self._net(x_tensor)
            probs  = torch.softmax(logits, dim=1)
        return probs.cpu().numpy()[0]


def _load_model():
    global _model, _train_mean, _train_std, _device, _n_features
    if _model is not None:
        return

    import torch

    _device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _train_mean = np.load(MEAN_PATH)
    _train_std  = np.load(STD_PATH)
    _n_features = len(_train_mean)
    _model      = _BiLSTMModel(MODEL_PATH, _device)


def _extract_features_from_video(video_path: str, seq_len: int = 30) -> np.ndarray:
    """
    Extract per-frame optical-flow features from a video.
    Produces exactly _n_features (42) features per frame to match the trained model.
    Returns array of shape (seq_len, n_features).
    """
    import cv2

    cap    = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray)
    cap.release()

    if len(frames) < 2:
        raise ValueError("Video too short — need at least 2 frames.")

    # Sample evenly to get seq_len frame pairs
    indices = np.linspace(0, len(frames) - 2, seq_len, dtype=int)

    feature_rows = []
    for idx in indices:
        curr = frames[min(idx,     len(frames) - 1)]
        nxt  = frames[min(idx + 1, len(frames) - 1)]

        flow = cv2.calcOpticalFlowFarneback(
            curr, nxt, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
        )
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # ── Build 42-feature vector ──────────────────────────────────────
        row = []

        # Global flow stats (10)
        row += [
            float(mag.mean()), float(mag.std()), float(mag.max()),
            float(mag.min()), float(np.percentile(mag, 25)),
            float(np.percentile(mag, 75)), float(np.percentile(mag, 90)),
            float(ang.mean()), float(ang.std()), float(np.percentile(ang, 75)),
        ]

        # Spatial quadrant stats — 4 quadrants × 4 stats = 16
        h, w = mag.shape
        quads = [
            mag[:h//2, :w//2], mag[:h//2, w//2:],
            mag[h//2:, :w//2], mag[h//2:, w//2:],
        ]
        for q in quads:
            row += [float(q.mean()), float(q.std()),
                    float(q.max()),  float(q.min())]

        # Frame-level intensity stats (8)
        row += [
            float(curr.mean()), float(curr.std()),
            float(curr.max()),  float(curr.min()),
            float(nxt.mean()),  float(nxt.std()),
            float(nxt.max()),   float(nxt.min()),
        ]

        # Motion direction histogram — 8 bins
        hist, _ = np.histogram(ang.flatten(), bins=8, range=(0, 2 * np.pi))
        hist    = hist.astype(float) / (hist.sum() + 1e-8)
        row    += hist.tolist()

        # Pad or trim to exactly _n_features
        while len(row) < _n_features:
            row.append(0.0)
        row = row[:_n_features]

        feature_rows.append(row)

    return np.array(feature_rows, dtype=np.float32)


def predict_horse_pain(video_path: str) -> dict:
    import torch

    _load_model()

    # Extract features
    features = _extract_features_from_video(video_path, seq_len=30)

    # Normalize
    features = (features - _train_mean) / (_train_std + 1e-8)

    # Run model
    x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(_device)
    probs = _model.predict(x)

    # probs[0] = No Pain, probs[1] = Pain Detected
    if len(probs) == 2:
        no_pain_prob   = float(probs[0])
        pain_prob      = float(probs[1])
    else:
        # Single output sigmoid
        pain_prob    = float(probs[0])
        no_pain_prob = 1.0 - pain_prob

    label      = "Pain Detected" if pain_prob > no_pain_prob else "No Pain"
    confidence = max(pain_prob, no_pain_prob)
    info       = BEHAVIOR_INFO[label]

    return {
        "prediction":          label,
        "confidence":          round(confidence * 100, 1),
        "pain_probability":    round(pain_prob * 100, 1),
        "no_pain_probability": round(no_pain_prob * 100, 1),
        "emoji":               info["emoji"],
        "color":               info["color"],
        "bg":                  info["bg"],
        "border":              info["border"],
        "description":         info["desc"],
        "advice":              info["advice"],
        "behavioral_indicators": info["indicators"],
    }
