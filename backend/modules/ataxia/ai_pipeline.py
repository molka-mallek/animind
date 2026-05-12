"""
Ataxia / Behavioral Disease Classification Pipeline
Uses ST-GCN (Spatial Temporal Graph Convolutional Network) to classify
dog gait from video into: Normal, Ataxia, or Hip Dysplasia.

Model architecture matches the training notebook exactly.
"""

import os
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from ultralytics import YOLO

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SEQUENCE_LENGTH = 30          # frames per inference window (matches training)
OVERLAP         = SEQUENCE_LENGTH // 2   # 50% sliding window overlap
NUM_JOINTS      = 17          # YOLO-Pose keypoints
NUM_COORDS      = 2           # x, y
CLASS_NAMES     = ["Normal", "Ataxia", "Hip Dysplasia"]
MIN_VALID_SEQS  = 1           # minimum sequences needed for a prediction

BASE_DIR   = Path(__file__).resolve().parent.parent.parent  # backend/
MODEL_DIR  = BASE_DIR / "model"
STGCN_PATH = MODEL_DIR / "stgcn_multiclass.pth"
ADJ_PATH   = MODEL_DIR / "adj_matrix.pt"
YOLO_PATH  = BASE_DIR / "yolo11n-pose.pt"

# ─────────────────────────────────────────────
# SKELETON GRAPH — YOLO-Pose 17-joint edges
# ─────────────────────────────────────────────
ANIMAL_EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (5, 11), (6, 12),
]


def build_adjacency(num_nodes: int, edges: list) -> torch.Tensor:
    """Normalised symmetric adjacency matrix (D^-0.5 A D^-0.5)."""
    adj = torch.eye(num_nodes)
    for i, j in edges:
        adj[i, j] = 1.0
        adj[j, i] = 1.0
    d = adj.sum(dim=1)
    d_inv_sqrt = torch.pow(d, -0.5)
    d_mat = torch.diag(d_inv_sqrt)
    return d_mat @ adj @ d_mat


# ─────────────────────────────────────────────
# MODEL ARCHITECTURE  — matches saved checkpoint keys exactly:
#   l1 (2→64), l2 (64→128), fc (128→num_classes)
#   No residual projections, no dropout in saved weights.
# ─────────────────────────────────────────────
class STGCN_Layer(nn.Module):
    def __init__(self, in_chan: int, out_chan: int):
        super().__init__()
        self.t_conv = nn.Conv2d(in_chan, out_chan, (1, 3), padding=(0, 1))
        self.s_conv = nn.Linear(out_chan, out_chan)
        self.bn     = nn.BatchNorm2d(out_chan)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # x: [B, C_in, N, T]
        x_t        = self.t_conv(x)               # [B, C_out, N, T]
        x_permuted = x_t.permute(0, 3, 2, 1)      # [B, T, N, C_out]
        x_g        = torch.matmul(adj, x_permuted) # [B, T, N, C_out]
        x_s        = self.s_conv(x_g)              # [B, T, N, C_out]
        return self.bn(x_s.permute(0, 3, 2, 1))    # [B, C_out, N, T]


class AnimalDiseaseSTGCN(nn.Module):
    def __init__(self, num_classes: int = 3):
        super().__init__()
        self.l1  = STGCN_Layer(2, 64)
        self.l2  = STGCN_Layer(64, 128)
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc  = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # x: [B, T, V, C] → [B, C, V, T]
        x = x.permute(0, 3, 2, 1)
        x = F.relu(self.l1(x, adj))
        x = F.relu(self.l2(x, adj))
        return self.fc(self.gap(x).view(x.size(0), -1))


# ─────────────────────────────────────────────
# LAZY-LOADED SINGLETONS
# ─────────────────────────────────────────────
_device    = "cuda" if torch.cuda.is_available() else "cpu"
_stgcn     = None
_adj       = None
_yolo_pose = None


def _load_models():
    global _stgcn, _adj, _yolo_pose

    if _stgcn is None:
        if not STGCN_PATH.exists():
            raise FileNotFoundError(f"ST-GCN weights not found: {STGCN_PATH}")
        model = AnimalDiseaseSTGCN(num_classes=3)
        state = torch.load(STGCN_PATH, map_location=_device)
        model.load_state_dict(state)
        model.to(_device)
        model.eval()
        _stgcn = model

    if _adj is None:
        if ADJ_PATH.exists():
            _adj = torch.load(ADJ_PATH, map_location=_device)
        else:
            # Rebuild from scratch if file missing
            _adj = build_adjacency(NUM_JOINTS, ANIMAL_EDGES).to(_device)

    if _yolo_pose is None:
        if not YOLO_PATH.exists():
            raise FileNotFoundError(f"YOLO pose model not found: {YOLO_PATH}")
        _yolo_pose = YOLO(str(YOLO_PATH))

    return _stgcn, _adj, _yolo_pose


# ─────────────────────────────────────────────
# KEYPOINT EXTRACTION
# ─────────────────────────────────────────────
def _extract_keypoints_from_video(video_path: str, yolo_pose) -> list:
    """
    Extract per-frame normalised keypoints [17, 2] from a video.
    Skips frames where no animal is detected.
    Returns list of np.ndarray each shaped (17, 2).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    keypoint_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = yolo_pose(frame, conf=0.15, verbose=False)
        res = results[0]

        if res.keypoints is None or len(res.keypoints.xyn) == 0:
            continue

        pts = res.keypoints.xyn[0].cpu().numpy()  # [17, 2]
        if pts.shape != (NUM_JOINTS, NUM_COORDS):
            continue

        # Mean-centre normalisation (matches training)
        pts = pts - pts.mean(axis=0)
        keypoint_frames.append(pts)

    cap.release()
    return keypoint_frames


def _build_sequences(keypoint_frames: list, seq_len: int, overlap: int) -> list:
    """Slide a window over keypoint frames to build fixed-length sequences."""
    sequences = []
    step = seq_len - overlap
    i = 0
    while i + seq_len <= len(keypoint_frames):
        seq = np.array(keypoint_frames[i: i + seq_len])  # [T, 17, 2]
        sequences.append(seq)
        i += step
    return sequences


# ─────────────────────────────────────────────
# PUBLIC INFERENCE FUNCTION
# ─────────────────────────────────────────────
def predict_ataxia(video_path: str) -> dict:
    """
    Run ST-GCN inference on a video file.

    Returns:
        {
            "prediction":  str,          # "Normal" | "Ataxia" | "Hip Dysplasia"
            "confidence":  float,        # 0.0 – 1.0
            "class_scores": {label: float, ...}
        }
    """
    stgcn, adj, yolo_pose = _load_models()

    # 1. Extract keypoints
    keypoint_frames = _extract_keypoints_from_video(video_path, yolo_pose)

    if len(keypoint_frames) < SEQUENCE_LENGTH:
        raise ValueError(
            f"Not enough pose frames detected ({len(keypoint_frames)} found, "
            f"{SEQUENCE_LENGTH} required). Ensure the animal is clearly visible "
            "throughout the video."
        )

    # 2. Build sliding-window sequences
    sequences = _build_sequences(keypoint_frames, SEQUENCE_LENGTH, OVERLAP)

    if len(sequences) < MIN_VALID_SEQS:
        raise ValueError("Could not build enough sequences from the video.")

    # 3. Batch inference
    batch = torch.tensor(np.array(sequences), dtype=torch.float32).to(_device)
    # batch: [N_seqs, T, V, C]

    with torch.no_grad():
        logits = stgcn(batch, adj)                        # [N_seqs, 3]
        probs  = F.softmax(logits, dim=1)                 # [N_seqs, 3]

    # 4. Average probabilities across all windows
    avg_probs = probs.mean(dim=0).cpu().numpy()           # [3]

    pred_idx    = int(np.argmax(avg_probs))
    prediction  = CLASS_NAMES[pred_idx]
    confidence  = float(avg_probs[pred_idx])
    class_scores = {CLASS_NAMES[i]: float(avg_probs[i]) for i in range(len(CLASS_NAMES))}

    return {
        "prediction":   prediction,
        "confidence":   confidence,
        "class_scores": class_scores,
    }
