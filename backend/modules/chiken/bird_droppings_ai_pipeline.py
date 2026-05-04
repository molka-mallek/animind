from pathlib import Path
import warnings

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

warnings.filterwarnings("ignore")

MODEL_PATH = Path(__file__).resolve().parent / "bird_droppings_resnet18_best.pth"
DEFAULT_CLASSES = ["coccii", "healthy"]
POSITIVE_CLASS_NAMES = {"coccii", "coccidiosis", "infected", "abnormal", "diseased", "positive"}
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location=device)

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        class_to_idx = checkpoint.get("class_to_idx")
    else:
        state_dict = checkpoint
        class_to_idx = None

    if isinstance(class_to_idx, dict) and class_to_idx:
        num_classes = len(class_to_idx)
        idx_to_class = {idx: name for name, idx in class_to_idx.items()}
    else:
        num_classes = int(state_dict["fc.weight"].shape[0])
        idx_to_class = {idx: DEFAULT_CLASSES[idx] for idx in range(num_classes)}

    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(512, num_classes)
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
            "Abnormal droppings color or consistency",
            "Possible blood or mucus traces",
            "Watery or foamy texture",
            "Signs that may correlate with intestinal infection",
        ],
        "description": "Possible abnormal droppings pattern detected",
        "recommendation": "Isolate affected birds and consult a veterinarian for stool test confirmation and treatment.",
        "emoji": "⚠️",
    },
    "normal": {
        "cues": [
            "Droppings appearance looks within normal range",
            "No obvious severe abnormal pattern detected",
        ],
        "description": "No obvious abnormal droppings pattern detected",
        "recommendation": "Continue monitoring flock health, feed quality, and hydration.",
        "emoji": "✅",
    },
}


def predict_bird_droppings(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to read image: {str(e)}"}

    img_tensor = transform(img).unsqueeze(0).to(device)

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
