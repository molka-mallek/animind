from pathlib import Path
from typing import cast
import warnings

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

warnings.filterwarnings("ignore")

MODEL_PATH = Path(__file__).resolve().parent / "fowlpox_efficientnet_b0_best.pth"
DEFAULT_CLASSES = ["healthy", "fowlpox"]
POSITIVE_CLASS_NAMES = {"fowlpox", "infected", "diseased", "sick", "positive"}
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_model_path():
    if MODEL_PATH.exists():
        return MODEL_PATH
    raise FileNotFoundError(f"Missing model checkpoint: {MODEL_PATH.name}")


def extract_state_dict_and_classes(checkpoint):
    if not isinstance(checkpoint, dict):
        return checkpoint, None

    if "model_state_dict" in checkpoint:
        return checkpoint["model_state_dict"], checkpoint.get("class_to_idx")

    if "state_dict" in checkpoint:
        return checkpoint["state_dict"], checkpoint.get("class_to_idx")

    return checkpoint, checkpoint.get("class_to_idx")


def infer_num_classes(state_dict):
    if "classifier.1.weight" in state_dict:
        return int(state_dict["classifier.1.weight"].shape[0])
    if "classifier.weight" in state_dict:
        return int(state_dict["classifier.weight"].shape[0])

    return len(DEFAULT_CLASSES)


def build_model(num_classes):
    model = models.efficientnet_b0(pretrained=False)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(1280, num_classes),
    )
    return model


def load_model():
    model_path = get_model_path()
    checkpoint = torch.load(model_path, map_location=device)
    state_dict, class_to_idx = extract_state_dict_and_classes(checkpoint)

    if isinstance(class_to_idx, dict) and class_to_idx:
        num_classes = len(class_to_idx)
        idx_to_class = {idx: name for name, idx in class_to_idx.items()}
    else:
        num_classes = infer_num_classes(state_dict)
        idx_to_class = {
            idx: (DEFAULT_CLASSES[idx] if idx < len(DEFAULT_CLASSES) else f"class_{idx}")
            for idx in range(num_classes)
        }

    model = build_model(num_classes)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model, idx_to_class


model, INDEX_TO_CLASS = load_model()

transform = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

CONDITION_KB = {
    "infected": {
        "cues": [
            "Visible skin lesions around comb, wattle, or eyelids",
            "Scab-like nodules on unfeathered skin",
            "Reduced activity and appetite",
            "Possible breathing discomfort in severe cases",
        ],
        "description": "Possible fowlpox signs detected",
        "recommendation": "Isolate affected birds, improve hygiene, and consult a poultry veterinarian quickly.",
        "emoji": "⚠️",
    },
    "normal": {
        "cues": [
            "No obvious pox-like lesions",
            "Normal skin appearance",
            "No clear signs of severe external infection",
        ],
        "description": "No obvious fowlpox signs detected",
        "recommendation": "Continue monitoring flock health and maintain vaccination and sanitation routines.",
        "emoji": "✅",
    },
}


def predict_fowlpox(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to read image: {str(e)}"}

    transformed = cast(torch.Tensor, transform(img))
    img_tensor = transformed.unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()

    pred_idx = int(np.argmax(probs))
    raw_label = str(INDEX_TO_CLASS.get(pred_idx, "healthy")).lower()
    condition = "infected" if raw_label in POSITIVE_CLASS_NAMES else "normal"
    confidence = float(probs[pred_idx])
    kb = CONDITION_KB[condition]

    return {
        "condition": condition,
        "raw_label": raw_label,
        "confidence": confidence,
        "emoji": kb["emoji"],
        "cues": kb["cues"],
        "description": kb["description"],
        "recommendation": kb["recommendation"],
        "probabilities": {
            str(INDEX_TO_CLASS[idx]).lower(): float(prob)
            for idx, prob in enumerate(probs)
        },
    }
