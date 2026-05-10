"""
Thermal Cat Health Screening — Ensemble pipeline for AniMind
Runs EfficientNet-B3 + ResNet50 + Custom CNN weighted soft-voting ensemble.
"""
from pathlib import Path
import warnings
import json
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

warnings.filterwarnings("ignore")

MODEL_DIR  = Path(__file__).resolve().parents[3] / "model" / "thermal_cat"
CONFIG     = json.load(open(MODEL_DIR / "inference_config.json"))
device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Pre-processing ───────────────────────────────────────────
p  = CONFIG["preprocessing"]
tf = transforms.Compose([
    transforms.Resize((p["img_size"], p["img_size"])),
    transforms.ToTensor(),
    transforms.Normalize(p["normalization_mean"], p["normalization_std"]),
])


# ── Custom CNN architecture (must match training) ────────────
class CatHealthCNN(nn.Module):
    def __init__(self):
        super().__init__()
        def conv_block(in_ch, out_ch):
            return nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 3, padding=1),
                nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
            )
        self.features   = nn.Sequential(
            conv_block(3, 32), conv_block(32, 64),
            conv_block(64, 128), conv_block(128, 256), conv_block(256, 512),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(512, 256), nn.ReLU(inplace=True), nn.Dropout(0.5),
            nn.Linear(256, 2),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


# ── Model loader ─────────────────────────────────────────────
def _load_model(name: str):
    path = MODEL_DIR / CONFIG["models"][name]["file"]
    if name == "custom_cnn":
        m = CatHealthCNN()
    elif name == "efficientnet_b3":
        m = models.efficientnet_b3(weights=None)
        n = m.classifier[1].in_features
        m.classifier = nn.Sequential(
            nn.Dropout(0.3), nn.Linear(n, 512), nn.ReLU(True),
            nn.Dropout(0.2), nn.Linear(512, 2),
        )
    elif name == "resnet50":
        m = models.resnet50(weights=None)
        n = m.fc.in_features
        m.fc = nn.Sequential(
            nn.Linear(n, 512), nn.ReLU(True),
            nn.Dropout(0.3), nn.Linear(512, 2),
        )
    m.load_state_dict(torch.load(path, map_location=device, weights_only=True))
    return m.to(device).eval()


# ── Singleton ensemble ───────────────────────────────────────
_ensemble = None


def _load():
    global _ensemble
    if _ensemble is not None:
        return
    _ensemble = {name: _load_model(name) for name in ["custom_cnn", "efficientnet_b3", "resnet50"]}


# ── Public API ───────────────────────────────────────────────
RECOMMENDATIONS = {
    "Healthy": "No thermal anomalies detected. Continue regular health monitoring.",
    "Sick":    "Thermal anomaly detected. Please consult a veterinarian for a full examination.",
}


def predict_thermal_cat(image_path: str) -> dict:
    _load()

    img_t     = tf(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    w         = CONFIG["ensemble"]["weights"]
    threshold = CONFIG["ensemble"]["threshold"]

    with torch.no_grad():
        probs_per_model = {}
        for name, mdl in _ensemble.items():
            sick_prob = torch.softmax(mdl(img_t), 1)[0, 1].item()
            probs_per_model[name] = round(sick_prob * 100, 1)

        sick_prob_ensemble = (
            w["custom_cnn"]      * (probs_per_model["custom_cnn"]      / 100) +
            w["efficientnet_b3"] * (probs_per_model["efficientnet_b3"] / 100) +
            w["resnet50"]        * (probs_per_model["resnet50"]         / 100)
        )

    pred      = 1 if sick_prob_ensemble >= threshold else 0
    label     = CONFIG["classes"][str(pred)]
    confidence = sick_prob_ensemble if pred == 1 else (1 - sick_prob_ensemble)

    return {
        "prediction":      label,
        "confidence":      round(confidence, 4),
        "sick_probability": round(sick_prob_ensemble * 100, 1),
        "healthy_probability": round((1 - sick_prob_ensemble) * 100, 1),
        "threshold":       round(threshold * 100, 1),
        "per_model":       probs_per_model,
        "emoji":           "✅" if label == "Healthy" else "⚠️",
        "recommendation":  RECOMMENDATIONS[label],
    }
