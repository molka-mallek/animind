"""
Fish Freshness AI Pipeline
Input : image path (str)
Output: freshness grade (C1/C2/C3), score (0-100), insights

Full pipeline:
  1. YOLO (yolo26n.pt)          — detect eye & gill bounding boxes
  2. SAM 2.1 (sam2.1_hiera_large.pt) — segment & crop each ROI
  3. DualStreamEfficientNet (fish_model.pth) — classify freshness

Architecture (DualStreamEfficientNet from training notebook):
  eye_crop  → EfficientNet-B0 (timm, num_classes=0) → 1280-d features
  gill_crop → EfficientNet-B0 (timm, num_classes=0) → 1280-d features
  concat (2560-d) → LayerNorm → Dropout(0.4) → Linear(2560,512)
                 → GELU → Dropout(0.2) → Linear(512,3)

Checkpoint format: wrapped dict with key 'model_state'
  config['class_names'] = ['C1', 'C2', 'C3']
  config['share_weights'] = False
  config['dropout'] = 0.4

Score ranges (from training notebook):
  C1: 85-100  (Very Fresh)
  C2: 40-84   (Moderately Fresh)
  C3: 0-39    (Not Fresh)

Fallback: if SAM2 is not installed, uses plain YOLO bounding-box crops.
Fallback: if YOLO finds no ROIs, uses centre-crop heuristic on the full image.
"""

from pathlib import Path
import warnings
import numpy as np
from PIL import Image

warnings.filterwarnings("ignore")

# ── Model paths ────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parents[2] / "model" / "fish_freshness"
YOLO_PATH      = _BASE / "yolo26n.pt"
SAM_CHECKPOINT = _BASE / "sam2.1_hiera_large.pt"
CLASSIFIER_PATH = _BASE / "fish_model.pth"

# ── Config (must match training) ───────────────────────────────────────────────
IMG_SIZE    = 224
CLASS_NAMES = ["C1", "C2", "C3"]
SCORE_RANGES = {
    "C1": (85, 100),
    "C2": (40, 84),
    "C3": (0,  39),
}
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

GRADE_KB = {
    "C1": {
        "label":          "Very Fresh",
        "emoji":          "🟢",
        "color":          {"bg": "#f0fdf4", "border": "#86efac", "text": "#16a34a"},
        "cues": [
            "Bright, clear and bulging eyes",
            "Vivid, shiny skin with metallic sheen",
            "Bright red or pink gills",
            "Firm flesh that springs back when pressed",
            "Fresh sea-like or neutral odour",
        ],
        "description":    "Excellent freshness — fish is at peak quality.",
        "recommendation": "Ideal for sashimi, sushi, or any preparation. Consume within 1–2 days.",
    },
    "C2": {
        "label":          "Moderately Fresh",
        "emoji":          "🟡",
        "color":          {"bg": "#fffbeb", "border": "#fcd34d", "text": "#d97706"},
        "cues": [
            "Slightly dull or sunken eyes",
            "Skin colour beginning to fade",
            "Gills turning pale pink or brownish",
            "Flesh slightly soft but still acceptable",
            "Mild fishy odour starting to develop",
        ],
        "description":    "Acceptable freshness — quality is declining.",
        "recommendation": "Cook thoroughly. Best consumed today; avoid raw preparations.",
    },
    "C3": {
        "label":          "Not Fresh",
        "emoji":          "🔴",
        "color":          {"bg": "#fef2f2", "border": "#fca5a5", "text": "#dc2626"},
        "cues": [
            "Cloudy, sunken or discoloured eyes",
            "Dull, discoloured or slimy skin",
            "Dark brown or grey gills",
            "Soft, mushy flesh that does not spring back",
            "Strong, unpleasant or ammonia-like odour",
        ],
        "description":    "Poor freshness — fish has deteriorated significantly.",
        "recommendation": "Do not consume. Discard the fish immediately.",
    },
}

# ── Lazy-loaded globals ────────────────────────────────────────────────────────
_yolo_model        = None
_yolo_error        = None
_sam_predictor     = None
_sam_error         = None
_classifier        = None
_classifier_error  = None
_device            = None
_val_transform     = None


# ── YOLO loader ────────────────────────────────────────────────────────────────
def _ensure_yolo():
    global _yolo_model, _yolo_error
    if _yolo_model is not None:
        return None
    if _yolo_error is not None:
        return _yolo_error
    try:
        from ultralytics import YOLO
        _yolo_model = YOLO(str(YOLO_PATH))
        return None
    except Exception as e:
        _yolo_error = str(e)
        return _yolo_error


# ── SAM 2.1 loader ────────────────────────────────────────────────────────────
def _ensure_sam():
    global _sam_predictor, _sam_error
    if _sam_predictor is not None:
        return None
    if _sam_error is not None:
        return _sam_error
    try:
        import torch
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        # SAM 2.1 hiera-large config name
        sam_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
        device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        sam_model = build_sam2(sam_cfg, str(SAM_CHECKPOINT), device=device)
        _sam_predictor = SAM2ImagePredictor(sam_model)
        return None
    except Exception as e:
        _sam_error = str(e)
        return _sam_error


# ── Classifier loader ─────────────────────────────────────────────────────────
def _ensure_classifier():
    global _classifier, _classifier_error, _device, _val_transform
    if _classifier is not None:
        return None
    if _classifier_error is not None:
        return _classifier_error
    try:
        import torch
        import torch.nn as nn
        import timm
        import torchvision.transforms as T

        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ── Rebuild DualStreamEfficientNet exactly as trained ──────────────────
        class DualStreamEfficientNet(nn.Module):
            def __init__(self, num_classes=3, dropout=0.4, share_weights=False):
                super().__init__()

                def make_backbone():
                    return timm.create_model(
                        "efficientnet_b0",
                        pretrained=False,
                        num_classes=0,
                        global_pool="avg",
                    )

                self.eye_stream  = make_backbone()
                self.gill_stream = self.eye_stream if share_weights else make_backbone()

                feat_dim  = self.eye_stream.num_features   # 1280
                fused_dim = feat_dim * 2                   # 2560

                self.classifier = nn.Sequential(
                    nn.LayerNorm(fused_dim),
                    nn.Dropout(p=dropout),
                    nn.Linear(fused_dim, 512),
                    nn.GELU(),
                    nn.Dropout(p=dropout / 2),
                    nn.Linear(512, num_classes),
                )

            def forward(self, eye, gill):
                f_eye  = self.eye_stream(eye)
                f_gill = self.gill_stream(gill)
                fused  = torch.cat([f_eye, f_gill], dim=1)
                return self.classifier(fused)

        # ── Load checkpoint ────────────────────────────────────────────────────
        ckpt = torch.load(str(CLASSIFIER_PATH), map_location=_device)

        # Checkpoint is a wrapped dict with key 'model_state'
        state_dict   = ckpt["model_state"]
        cfg          = ckpt.get("config", {})
        dropout      = cfg.get("dropout", 0.4)
        share_weights = cfg.get("share_weights", False)

        net = DualStreamEfficientNet(
            num_classes=len(CLASS_NAMES),
            dropout=dropout,
            share_weights=share_weights,
        )
        net.load_state_dict(state_dict)
        net.to(_device)
        net.eval()
        _classifier = net

        # Inference transform (val_transforms from training)
        _val_transform = T.Compose([
            T.Resize((IMG_SIZE, IMG_SIZE)),
            T.ToTensor(),
            T.Normalize(mean=MEAN, std=STD),
        ])
        return None
    except Exception as e:
        _classifier_error = str(e)
        return _classifier_error


# ── ROI detection helpers ──────────────────────────────────────────────────────
def _detect_rois(image_path: str):
    """
    Run YOLO on the image and return (eye_box, gill_box) as
    (x1, y1, x2, y2) pixel coords, or None if not found.
    """
    err = _ensure_yolo()
    if err:
        return None, None, f"YOLO unavailable: {err}"

    results = _yolo_model(image_path, verbose=False)
    eye_box  = None
    gill_box = None

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            cls_name = _yolo_model.names.get(cls_id, "").lower()
            coords = box.xyxy[0].cpu().numpy().astype(int)
            if "eye" in cls_name and eye_box is None:
                eye_box = tuple(coords)
            elif "gill" in cls_name and gill_box is None:
                gill_box = tuple(coords)

    return eye_box, gill_box, None


def _crop_with_sam(image_np, box):
    """
    Use SAM 2.1 to segment the ROI defined by box, then crop the masked region.
    Falls back to plain bounding-box crop if SAM is unavailable.
    """
    sam_err = _ensure_sam()
    if sam_err:
        # Fallback: plain bbox crop
        x1, y1, x2, y2 = box
        crop = image_np[y1:y2, x1:x2]
        return Image.fromarray(crop)

    import numpy as np
    _sam_predictor.set_image(image_np)
    input_box = np.array([[box[0], box[1], box[2], box[3]]])
    masks, scores, _ = _sam_predictor.predict(
        point_coords=None,
        point_labels=None,
        box=input_box,
        multimask_output=False,
    )
    mask = masks[0].astype(np.uint8)

    # Apply mask and crop to bounding box
    x1, y1, x2, y2 = box
    masked = image_np.copy()
    masked[mask == 0] = 0
    crop = masked[y1:y2, x1:x2]
    return Image.fromarray(crop)


def _centre_crop(img: Image.Image, fraction=0.4) -> Image.Image:
    """Fallback: take a centre crop of the image."""
    w, h = img.size
    cw, ch = int(w * fraction), int(h * fraction)
    left = (w - cw) // 2
    top  = (h - ch) // 2
    return img.crop((left, top, left + cw, top + ch))


def _grade_to_score(grade: str, confidence: float) -> int:
    lo, hi = SCORE_RANGES[grade]
    t = float(np.clip((confidence - 0.5) / 0.5, 0, 1))
    return int(round(lo + t * (hi - lo)))


# ── Public API ─────────────────────────────────────────────────────────────────
def predict_fish_freshness(image_path: str) -> dict:
    # 1. Load classifier (required)
    cls_err = _ensure_classifier()
    if cls_err:
        return {"error": f"Fish freshness classifier unavailable: {cls_err}"}

    try:
        import torch
        img_pil = Image.open(image_path).convert("RGB")
        img_np  = np.array(img_pil)

        # 2. Detect ROIs with YOLO
        eye_box, gill_box, yolo_err = _detect_rois(image_path)

        # 3. Crop ROIs (SAM if available, else bbox, else centre-crop)
        if eye_box is not None:
            eye_crop = _crop_with_sam(img_np, eye_box)
        else:
            # No eye detected — use left-centre crop as proxy
            w, h = img_pil.size
            eye_crop = img_pil.crop((0, h // 4, w // 2, 3 * h // 4))

        if gill_box is not None:
            gill_crop = _crop_with_sam(img_np, gill_box)
        else:
            # No gill detected — use right-centre crop as proxy
            w, h = img_pil.size
            gill_crop = img_pil.crop((w // 2, h // 4, w, 3 * h // 4))

        # 4. Transform crops
        eye_tensor  = _val_transform(eye_crop.convert("RGB")).unsqueeze(0).to(_device)
        gill_tensor = _val_transform(gill_crop.convert("RGB")).unsqueeze(0).to(_device)

        # 5. Run classifier
        with torch.no_grad():
            logits      = _classifier(eye_tensor, gill_tensor)
            prob_tensor = torch.softmax(logits, dim=1)[0].cpu().numpy()

        pred_idx   = int(np.argmax(prob_tensor))
        grade      = CLASS_NAMES[pred_idx]
        confidence = float(prob_tensor[pred_idx])
        probs      = {CLASS_NAMES[i]: float(prob_tensor[i]) for i in range(len(CLASS_NAMES))}
        score      = _grade_to_score(grade, confidence)

        kb = GRADE_KB[grade]

        # Note whether ROIs were detected or fallback crops were used
        roi_status = "yolo+sam" if (eye_box and gill_box and _sam_predictor) else \
                     "yolo_bbox" if (eye_box and gill_box) else \
                     "centre_crop_fallback"

        return {
            "grade":          grade,
            "label":          kb["label"],
            "score":          score,
            "confidence":     confidence,
            "emoji":          kb["emoji"],
            "color":          kb["color"],
            "cues":           kb["cues"],
            "description":    kb["description"],
            "recommendation": kb["recommendation"],
            "probabilities":  probs,
            "roi_status":     roi_status,
        }

    except Exception as e:
        return {"error": f"Inference failed: {str(e)}"}
