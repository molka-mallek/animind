"""
Thermal Cat Classification — AI Pipeline
Ensemble of Custom CNN + EfficientNet-B3 + ResNet50 for Healthy vs Sick.
Runs in the main backend venv (torch + torchvision + Pillow required).
"""
import os
import json
import numpy as np
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "model", "thermal_cat")

CONFIG_PATH = os.path.join(MODEL_DIR, "inference_config.json")

with open(CONFIG_PATH) as f:
    _cfg = json.load(f)

CLASSES   = _cfg["classes"]          # {"0": "Healthy", "1": "Sick"}
THRESHOLD = _cfg["ensemble"]["threshold"]
WEIGHTS   = _cfg["ensemble"]["weights"]
PREP      = _cfg["preprocessing"]

RESULT_INFO = {
    "Healthy": {
        "emoji":  "✅",
        "color":  "#16a34a",
        "bg":     "#f0fdf4",
        "border": "#86efac",
        "desc":   "No significant health concerns detected in the thermal image.",
        "advice": "Cat appears healthy. Continue regular veterinary check-ups and monitoring.",
    },
    "Sick": {
        "emoji":  "⚠️",
        "color":  "#dc2626",
        "bg":     "#fef2f2",
        "border": "#fca5a5",
        "desc":   "Potential health concern detected via thermal imaging analysis.",
        "advice": "🚨 Consult a licensed veterinarian. This is a screening tool — not a diagnosis.",
    },
}

# ── Model definitions ──────────────────────────────────────────────────────
def _build_custom_cnn():
    import torch.nn as nn
    def conv_block(in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
    class CatHealthCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
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
    return CatHealthCNN()


def _build_efficientnet_b3():
    from torchvision import models
    import torch.nn as nn
    m = models.efficientnet_b3(weights=None)
    n = m.classifier[1].in_features
    m.classifier = nn.Sequential(
        nn.Dropout(0.3), nn.Linear(n, 512),
        nn.ReLU(True), nn.Dropout(0.2), nn.Linear(512, 2),
    )
    return m


def _build_resnet50():
    from torchvision import models
    import torch.nn as nn
    m = models.resnet50(weights=None)
    n = m.fc.in_features
    m.fc = nn.Sequential(
        nn.Linear(n, 512), nn.ReLU(True),
        nn.Dropout(0.3), nn.Linear(512, 2),
    )
    return m


# ── Lazy-loaded models ─────────────────────────────────────────────────────
_models  = {}
_device  = None
_transform = None


def _load_models():
    global _models, _device, _transform
    if _models:
        return

    import torch
    from torchvision import transforms

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    builders = {
        "custom_cnn":      (_build_custom_cnn,      "custom_cnn.pth"),
        "efficientnet_b3": (_build_efficientnet_b3, "efficientnet_b3.pth"),
        "resnet50":        (_build_resnet50,         "resnet50.pth"),
    }

    for name, (builder, fname) in builders.items():
        path = os.path.join(MODEL_DIR, fname)
        m = builder()
        m.load_state_dict(
            torch.load(path, map_location=_device, weights_only=True)
        )
        m.to(_device).eval()
        _models[name] = m

    _transform = transforms.Compose([
        transforms.Resize((PREP["img_size"], PREP["img_size"])),
        transforms.ToTensor(),
        transforms.Normalize(PREP["normalization_mean"], PREP["normalization_std"]),
    ])


def predict_thermal_cat(image_path: str) -> dict:
    import torch
    from PIL import Image

    _load_models()

    img_t = _transform(Image.open(image_path).convert("RGB")).unsqueeze(0).to(_device)

    with torch.no_grad():
        cp = torch.softmax(_models["custom_cnn"](img_t),      1)[0, 1].item()
        ep = torch.softmax(_models["efficientnet_b3"](img_t), 1)[0, 1].item()
        rp = torch.softmax(_models["resnet50"](img_t),        1)[0, 1].item()

    sick_prob = (
        WEIGHTS["custom_cnn"]      * cp +
        WEIGHTS["efficientnet_b3"] * ep +
        WEIGHTS["resnet50"]        * rp
    )

    pred      = 1 if sick_prob >= THRESHOLD else 0
    label     = CLASSES[str(pred)]
    confidence = sick_prob if pred == 1 else (1.0 - sick_prob)
    info      = RESULT_INFO[label]

    return {
        "prediction":       label,
        "confidence":       round(confidence * 100, 1),
        "sick_probability": round(sick_prob * 100, 1),
        "healthy_probability": round((1 - sick_prob) * 100, 1),
        "threshold":        round(THRESHOLD * 100, 1),
        "model_type":       "ensemble",
        "emoji":            info["emoji"],
        "color":            info["color"],
        "bg":               info["bg"],
        "border":           info["border"],
        "description":      info["desc"],
        "advice":           info["advice"],
        "model_scores": {
            "custom_cnn":      round(cp * 100, 1),
            "efficientnet_b3": round(ep * 100, 1),
            "resnet50":        round(rp * 100, 1),
        },
    }
