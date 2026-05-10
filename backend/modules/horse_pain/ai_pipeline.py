"""
Horse Pain Detection — BiLSTM pipeline for AniMind
Extracts optical-flow motion features from video and runs BiLSTM inference.

Architecture exactly mirrors the trained checkpoint:
  lstm : 2-layer bidirectional LSTM, input=42, hidden=64
  attn : BahdanauAttention(128)  — Linear(128→1) + softmax
  fc   : Linear(128,64) → ReLU → Dropout → Linear(64,2)

Feature extraction: 3×2 spatial grid × 7 stats = 42 features/frame
"""
from pathlib import Path
import warnings
import tempfile
import numpy as np
import torch
import torch.nn as nn
import cv2

warnings.filterwarnings("ignore")

MODEL_DIR    = Path(__file__).resolve().parents[3] / "model" / "horse_pain"
HORSE_INPUT  = 42
HORSE_HIDDEN = 64
HORSE_LAYERS = 2
HORSE_CLASSES = ["Healthy", "Distressed"]
device = torch.device("cpu")


# ── Architecture (matches checkpoint exactly) ────────────────
class BahdanauAttention(nn.Module):
    """Single-head additive attention over LSTM sequence outputs."""
    def __init__(self, hidden_size: int):
        super().__init__()
        self.attn = nn.Linear(hidden_size, 1, bias=True)

    def forward(self, lstm_out):            # (B, T, H)
        scores  = self.attn(lstm_out)       # (B, T, 1)
        weights = torch.softmax(scores, dim=1)  # (B, T, 1)
        context = (weights * lstm_out).sum(dim=1)  # (B, H)
        return context, weights.squeeze(-1)


class HorseBiLSTM(nn.Module):
    def __init__(self,
                 input_size=HORSE_INPUT,
                 hidden_size=HORSE_HIDDEN,
                 num_layers=HORSE_LAYERS,
                 num_classes=2,
                 dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.attn = BahdanauAttention(hidden_size * 2)   # 128
        self.fc   = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):                  # x: (B, T, 42)
        out, _      = self.lstm(x)         # (B, T, 128)
        context, _  = self.attn(out)       # (B, 128)
        logits      = self.fc(context)     # (B, 2)
        return logits, None


# ── Singleton load ───────────────────────────────────────────
_model = None
_mean  = None
_std   = None


def _load():
    global _model, _mean, _std
    if _model is not None:
        return
    _model = HorseBiLSTM()
    state  = torch.load(MODEL_DIR / "behavior_bilstm.pt",
                        map_location=device, weights_only=True)
    _model.load_state_dict(state)
    _model.eval()
    _mean = np.load(MODEL_DIR / "train_mean.npy").astype(np.float32)  # (42,)
    _std  = np.load(MODEL_DIR / "train_std.npy" ).astype(np.float32)  # (42,)
    _std  = np.where(_std < 1e-8, 1.0, _std)                          # avoid div/0


# ── Feature extraction (3×2 grid × 7 stats = 42) ────────────
def _video_to_sequence(video_path: str, num_frames: int = 60) -> np.ndarray:
    cap   = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        raise ValueError("Cannot read video — 0 frames found.")

    indices = np.linspace(0, total - 1, num=min(num_frames, total), dtype=int)
    frames_gray = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (128, 128))
        frames_gray.append(gray)
    cap.release()

    if len(frames_gray) < 2:
        raise ValueError("Not enough readable frames in video.")

    features = []
    prev = frames_gray[0].astype(np.float32)
    for curr_gray in frames_gray[1:]:
        curr = curr_gray.astype(np.float32)
        flow = cv2.calcOpticalFlowFarneback(
            prev, curr, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )  # (128, 128, 2)

        # 3 rows × 2 cols × 7 stats = 42 features
        h, w = flow.shape[:2]
        row_feats = []
        for row in range(3):
            for col in range(2):
                r0, r1 = row * h // 3, (row + 1) * h // 3
                c0, c1 = col * w // 2, (col + 1) * w // 2
                patch  = flow[r0:r1, c0:c1]
                fx, fy = patch[..., 0], patch[..., 1]
                mag    = np.sqrt(fx**2 + fy**2)
                ang    = np.arctan2(fy, fx)
                row_feats.extend([
                    float(fx.mean()), float(fx.std()),
                    float(fy.mean()), float(fy.std()),
                    float(mag.mean()), float(mag.std()),
                    float(ang.mean())
                ])
        features.append(row_feats)   # 6 × 7 = 42  ✓
        prev = curr

    return np.array(features, dtype=np.float32)   # (T-1, 42)


# ── Recommendations ──────────────────────────────────────────
RECOMMENDATIONS = {
    "Healthy":    "Horse appears to be moving normally. Continue regular monitoring.",
    "Distressed": "Signs of possible pain or distress detected. Please consult a veterinarian.",
}


# ── Public API ───────────────────────────────────────────────
def predict_horse_pain(video_path: str) -> dict:
    _load()
    seq = _video_to_sequence(video_path)      # (T, 42) raw
    seq = (seq - _mean) / _std                # normalise
    x   = torch.tensor(seq[np.newaxis], dtype=torch.float32)   # (1, T, 42)

    with torch.no_grad():
        logits, _ = _model(x)
        probs     = torch.softmax(logits, dim=1)[0].cpu().numpy()

    pred_idx   = int(np.argmax(probs))
    prediction = HORSE_CLASSES[pred_idx]
    confidence = float(probs[pred_idx])

    return {
        "prediction":     prediction,
        "confidence":     round(confidence, 4),
        "probabilities":  {
            HORSE_CLASSES[0]: round(float(probs[0]), 4),
            HORSE_CLASSES[1]: round(float(probs[1]), 4),
        },
        "emoji":          "✅" if prediction == "Healthy" else "⚠️",
        "recommendation": RECOMMENDATIONS[prediction],
        "video_info":     {"seq_len": len(seq)},
    }
