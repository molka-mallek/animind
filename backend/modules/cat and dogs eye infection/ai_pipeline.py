from pathlib import Path
import warnings

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

warnings.filterwarnings("ignore")

MODEL_PATH = Path(__file__).resolve().parent / "cat_eye_infection_resnet18_best.pth"
DEFAULT_CLASSES = ["healthy", "infected"]
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    class_to_idx = (
        checkpoint.get("class_to_idx")
        if isinstance(checkpoint, dict)
        else None
    )
    if isinstance(class_to_idx, dict) and class_to_idx:
        num_classes = len(class_to_idx)
        idx_to_class = {idx: name for name, idx in class_to_idx.items()}
    else:
        num_classes = len(DEFAULT_CLASSES)
        idx_to_class = {idx: name for idx, name in enumerate(DEFAULT_CLASSES)}

    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(512, num_classes)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint
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
            "Redness or inflammation",
            "Discharge (clear, yellow, or green)",
            "Swelling around the eye",
            "Cloudiness or opacity",
            "Squinting or excessive blinking",
        ],
        "description": "Signs of possible eye infection detected",
        "recommendation": "Please consult a veterinarian as soon as possible for proper diagnosis and treatment.",
        "emoji": "⚠️",
    },
    "normal": {
        "cues": [
            "Clear and bright appearance",
            "No visible discharge",
            "Normal eye opening and closure",
            "Symmetrical appearance",
            "No signs of swelling",
        ],
        "description": "Eye appears healthy",
        "recommendation": "Continue regular eye care and monitor for any changes.",
        "emoji": "✅",
    },
}


def predict_eye_infection(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to read image: {str(e)}"}

    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()

    pred_idx = int(np.argmax(probs))
    raw_condition = str(INDEX_TO_CLASS.get(pred_idx, "healthy")).lower()
    condition = "infected" if raw_condition == "infected" else "normal"
    confidence = float(probs[pred_idx])
    kb = CONDITION_KB[condition]

    infected_idx = next(
        (idx for idx, name in INDEX_TO_CLASS.items() if str(name).lower() == "infected"),
        None,
    )
    healthy_idx = next(
        (idx for idx, name in INDEX_TO_CLASS.items() if str(name).lower() in {"healthy", "normal"}),
        None,
    )
    infected_prob = float(probs[infected_idx]) if infected_idx is not None else 0.0
    normal_prob = float(probs[healthy_idx]) if healthy_idx is not None else 0.0

    return {
        "condition": condition,
        "confidence": confidence,
        "emoji": kb["emoji"],
        "cues": kb["cues"],
        "description": kb["description"],
        "recommendation": kb["recommendation"],
        "probabilities": {
            "infected": infected_prob,
            "normal": normal_prob,
        },
    }
