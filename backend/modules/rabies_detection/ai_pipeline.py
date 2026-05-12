from pathlib import Path
import warnings

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

warnings.filterwarnings("ignore")

MODEL_PATH = Path(__file__).resolve().parent / "rabies_efficientnet_b0_best.pth"
CLASS_NAMES = ["normal", "rabies"]
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    model = models.efficientnet_b0(pretrained=False)
    
    # Rebuild the exact classifier architecture from your notebook
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(1280, 256),        # layer 1 → 256
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, len(CLASS_NAMES))  # layer 4 → 2 classes
    )

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


model = load_model()

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


def predict_rabies(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to read image: {str(e)}"}

    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()

    pred_idx = int(np.argmax(probs))
    raw_label = CLASS_NAMES[pred_idx]
    label = "rage" if raw_label == "rabies" else "normal"
    confidence = float(probs[pred_idx])

    return {"label": label, "confidence": confidence}
