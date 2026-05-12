"""
Skin Anomaly Detection Pipeline
================================
Pipeline complet :
  1. Classification  → Chat (cat) ou Chien (dog)
  2. Détection       → Sain (healthy) ou Anomalie cutanée (anomaly)
  3. Segmentation    → U-Net : localisation de la zone anormale (si anomalie)

Modèles requis (placer dans backend/model/) :
  - best_classifier.h5          (VGG16 / ResNet50 / EfficientNet / CNN)
  - best_anomaly_detector.h5    (idem)
  - unet_segmentation.h5        (U-Net + Attention Gates)
"""

from pathlib import Path
import warnings
import base64
import io

import numpy as np
import cv2
from PIL import Image

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "model"

CLASSIFIER_PATH      = MODEL_DIR / "best_classifier.h5"
ANOMALY_DET_PATH     = MODEL_DIR / "best_anomaly_detector.h5"
UNET_PATH            = MODEL_DIR / "unet_segmentation.h5"
METADATA_PATH        = MODEL_DIR / "skin_anomaly_metadata.json"

# ── Config ─────────────────────────────────────────────────────────────────
IMG_SIZE = (224, 224)

# Default class mapping (overridden by metadata if available)
DEFAULT_CLASS_INDICES = {"cats": 0, "dogs": 1}   # cat=0, dog=1
DEFAULT_ANOMALY_IDX   = 0                          # 0 = anomaly class (per metadata)

# ── Knowledge base ─────────────────────────────────────────────────────────
ANIMAL_KB = {
    "cats": {"emoji": "🐱", "label": "Cat"},
    "dogs": {"emoji": "🐶", "label": "Dog"},
    # fallback keys
    "cat":  {"emoji": "🐱", "label": "Cat"},
    "dog":  {"emoji": "🐶", "label": "Dog"},
}

ANOMALY_KB = {
    "anomaly": {
        "emoji": "⚠️",
        "label": "Skin Anomaly Detected",
        "description": "Signs of a possible skin condition have been detected.",
        "cues": [
            "Unusual skin texture or discoloration",
            "Possible lesion, rash, or irritation",
            "Abnormal pigmentation pattern",
            "Potential inflammation or swelling",
            "Area of concern identified by segmentation",
        ],
        "recommendation": (
            "Please consult a veterinarian as soon as possible. "
            "Early diagnosis improves treatment outcomes significantly."
        ),
    },
    "healthy": {
        "emoji": "✅",
        "label": "Healthy Skin",
        "description": "No visible skin anomaly detected.",
        "cues": [
            "Uniform coat and skin appearance",
            "No visible lesions or discoloration",
            "Normal skin texture",
            "No signs of inflammation",
            "Coat appears healthy and intact",
        ],
        "recommendation": (
            "Your pet's skin looks healthy. "
            "Continue regular grooming and schedule routine vet check-ups."
        ),
    },
}

# ── Lazy-loaded models ──────────────────────────────────────────────────────
_classifier      = None
_anomaly_det     = None
_unet            = None
_class_indices   = None
_anomaly_idx     = None
_load_error      = None


def _load_models():
    """Load all three Keras models. Called once on first prediction."""
    global _classifier, _anomaly_det, _unet
    global _class_indices, _anomaly_idx, _load_error

    if _load_error is not None:
        raise RuntimeError(_load_error)
    if _classifier is not None:
        return  # already loaded

    import json
    import tensorflow as tf

    # ── Custom loss needed to load U-Net ──────────────────────────────────
    def dice_loss(y_true, y_pred, smooth=1e-6):
        y_true_f = tf.keras.backend.flatten(tf.cast(y_true, tf.float32))
        y_pred_f = tf.keras.backend.flatten(tf.cast(y_pred, tf.float32))
        intersection = tf.reduce_sum(y_true_f * y_pred_f)
        return 1 - (2. * intersection + smooth) / (
            tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth
        )

    def bce_dice_loss(y_true, y_pred):
        return tf.keras.losses.binary_crossentropy(y_true, y_pred) + dice_loss(y_true, y_pred)

    custom_objects = {"bce_dice_loss": bce_dice_loss, "dice_loss": dice_loss}

    try:
        # Load metadata (class indices, anomaly index)
        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r") as f:
                meta = json.load(f)
            _class_indices = meta.get("classification_classes", DEFAULT_CLASS_INDICES)
            _anomaly_idx   = int(meta.get("anomaly_idx", DEFAULT_ANOMALY_IDX))
        else:
            _class_indices = DEFAULT_CLASS_INDICES
            _anomaly_idx   = DEFAULT_ANOMALY_IDX

        # Load classifier
        if not CLASSIFIER_PATH.exists():
            raise FileNotFoundError(f"Classifier model not found: {CLASSIFIER_PATH}")
        _classifier = tf.keras.models.load_model(str(CLASSIFIER_PATH), compile=False)

        # Load anomaly detector
        if not ANOMALY_DET_PATH.exists():
            raise FileNotFoundError(f"Anomaly detector model not found: {ANOMALY_DET_PATH}")
        _anomaly_det = tf.keras.models.load_model(str(ANOMALY_DET_PATH), compile=False)

        # Load U-Net (requires custom loss)
        if not UNET_PATH.exists():
            raise FileNotFoundError(f"U-Net model not found: {UNET_PATH}")
        _unet = tf.keras.models.load_model(
            str(UNET_PATH),
            custom_objects=custom_objects,
            compile=False,
        )

    except Exception as e:
        _load_error = str(e)
        raise


# ── Image preprocessing ────────────────────────────────────────────────────
def _preprocess(image_path: str) -> np.ndarray:
    """Load and normalize image → (1, 224, 224, 3) float32."""
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0), arr


# ── Segmentation mask → base64 PNG ────────────────────────────────────────
def _mask_to_base64(mask_2d: np.ndarray, original_arr: np.ndarray, visualization_type: str = "medical") -> tuple:
    """
    Overlay the segmentation mask on the original image and return
    the result as a base64-encoded PNG string + the filtered mask for area calculation.
    
    Args:
        mask_2d: 2D segmentation mask
        original_arr: Original image array
        visualization_type: "medical" (recommended), "heatmap", "contour", "bbox", or "circle"
        
    Returns:
        tuple: (base64_image_string, filtered_mask_2d)
    """
    # Resize mask to IMG_SIZE just in case
    mask_resized = cv2.resize(mask_2d, IMG_SIZE)
    img_uint8 = np.uint8(original_arr * 255)
    
    # Variable pour stocker le masque filtré final
    final_filtered_mask = None
    
    if visualization_type == "medical":
        # ═══════════════════════════════════════════════════════════════════════
        # SOLUTION RADICALE: Détection multi-méthodes pour segmentation précise
        # ═══════════════════════════════════════════════════════════════════════
        overlay = img_uint8.copy()
        
        # ── MÉTHODE 1: Détection basée sur la couleur (HSV) ──
        hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV)
        
        # Plages OPTIMISÉES pour capturer toutes les lésions roses/rouges
        # Rouge vif (inflammations)
        lower_red1 = np.array([0, 50, 60])
        upper_red1 = np.array([12, 255, 255])
        lower_red2 = np.array([168, 50, 60])
        upper_red2 = np.array([180, 255, 255])
        
        # Rose/Orange (lésions) - Plage élargie pour capturer toutes les nuances
        lower_pink = np.array([0, 30, 80])
        upper_pink = np.array([20, 220, 255])
        
        # Créer les masques (SANS le masque brun pour éviter le pelage)
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
        
        # Combiner uniquement rouge et rose (pas de brun)
        color_mask = cv2.bitwise_or(mask_red1, mask_red2)
        color_mask = cv2.bitwise_or(color_mask, mask_pink)
        
        # ── MÉTHODE 2: Détection de texture (variance locale) ──
        gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY)
        total_area = IMG_SIZE[0] * IMG_SIZE[1]  # Définir total_area ici
        
        # Calculer la variance locale (zones anormales ont souvent texture différente)
        kernel_size = 7
        mean = cv2.blur(gray, (kernel_size, kernel_size))
        mean_sq = cv2.blur(gray**2, (kernel_size, kernel_size))
        variance = mean_sq - mean**2
        
        # Normaliser et seuiller
        variance_norm = cv2.normalize(variance, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        _, texture_mask = cv2.threshold(variance_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # ── MÉTHODE 3: Utiliser le masque U-Net avec seuil modéré ──
        # Utiliser un seuil plus bas pour capturer plus de la lésion
        unet_mask = (mask_resized > 0.60).astype(np.uint8) * 255
        
        # ── FUSION DES MÉTHODES (APPROCHE ÉQUILIBRÉE) ──
        # Utiliser l'union (OR) de la couleur et U-Net pour ne rien manquer
        combined_mask = cv2.bitwise_or(color_mask, unet_mask)
        
        # Si le masque combiné est trop grand (>40%), utiliser seulement la couleur
        if cv2.countNonZero(combined_mask) > (total_area * 0.40):
            combined_mask = color_mask
            # Si la couleur seule est vide, utiliser U-Net avec seuil plus élevé
            if cv2.countNonZero(combined_mask) < 100:
                combined_mask = (mask_resized > 0.75).astype(np.uint8) * 255
        
        # ── NETTOYAGE MORPHOLOGIQUE MODÉRÉ ──
        # Éliminer le bruit
        kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_small, iterations=1)
        
        # Fermer les petits trous
        kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_large, iterations=2)
        
        # ── EXTRACTION DES CONTOURS ──
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # ── FILTRAGE INTELLIGENT DES CONTOURS ──
        min_area = 80      # Minimum 80 pixels (environ 0.16% de l'image)
        max_area = total_area * 0.25  # Maximum 25% de l'image (pour capturer les grandes lésions)
        
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Vérifier la circularité (les lésions sont souvent arrondies)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    # Accepter les formes avec circularité > 0.2 (formes relativement compactes)
                    if circularity > 0.2:
                        valid_contours.append(contour)
        
        # Trier par taille et garder les 5 plus grandes zones (pour capturer toute la lésion)
        if len(valid_contours) > 5:
            valid_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)[:5]
        
        # ── VISUALISATION MÉDICALE PROFESSIONNELLE ──
        if len(valid_contours) > 0:
            # Créer un masque binaire pour le calcul de la zone
            final_filtered_mask = np.zeros(IMG_SIZE, dtype=np.uint8)
            for contour in valid_contours:
                cv2.fillPoly(final_filtered_mask, [contour], 255)
            
            # Créer un masque overlay semi-transparent
            mask_overlay = np.zeros_like(overlay)
            
            for contour in valid_contours:
                # Remplissage rouge semi-transparent
                cv2.fillPoly(mask_overlay, [contour], (255, 70, 70))
            
            # Fusionner avec l'image originale (70% original, 30% overlay)
            overlay = cv2.addWeighted(overlay, 0.7, mask_overlay, 0.3, 0)
            
            # Dessiner les contours avec bordure épaisse
            for contour in valid_contours:
                # Contour rouge vif
                cv2.drawContours(overlay, [contour], -1, (220, 20, 20), 3)
                
                # Ajouter un contour blanc externe pour meilleur contraste
                cv2.drawContours(overlay, [contour], -1, (255, 255, 255), 1)
                
                # Ajouter des marqueurs aux coins du bounding box
                x, y, w, h = cv2.boundingRect(contour)
                corner_len = min(12, w // 5, h // 5)
                
                # Coins jaunes pour visibilité
                corners = [
                    ((x, y), (x + corner_len, y), (x, y + corner_len)),  # Top-left
                    ((x + w, y), (x + w - corner_len, y), (x + w, y + corner_len)),  # Top-right
                    ((x, y + h), (x + corner_len, y + h), (x, y + h - corner_len)),  # Bottom-left
                    ((x + w, y + h), (x + w - corner_len, y + h), (x + w, y + h - corner_len))  # Bottom-right
                ]
                
                for corner_pts in corners:
                    cv2.line(overlay, corner_pts[0], corner_pts[1], (255, 220, 0), 3)
                    cv2.line(overlay, corner_pts[0], corner_pts[2], (255, 220, 0), 3)
        else:
            # Aucun contour valide trouvé
            final_filtered_mask = np.zeros(IMG_SIZE, dtype=np.uint8)
    
    elif visualization_type == "heatmap":
        # Original heatmap overlay
        heatmap = cv2.applyColorMap(np.uint8(255 * mask_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(img_uint8, 0.55, heatmap, 0.45, 0)
        
    elif visualization_type == "contour":
        # Contour-based visualization - trace les contours exacts des anomalies
        overlay = img_uint8.copy()
        
        # Create binary mask with adjustable threshold
        binary_mask = (mask_resized > 0.6).astype(np.uint8)
        
        # Apply morphological operations to clean the mask
        kernel = np.ones((3, 3), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours with thick red lines - only significant ones
        min_area = 50
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                # Draw thick red contour
                cv2.drawContours(overlay, [contour], -1, (255, 0, 0), 3)
                
        # Add semi-transparent fill for detected anomalies
        mask_colored = np.zeros_like(overlay)
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                cv2.fillPoly(mask_colored, [contour], (255, 100, 100))
        overlay = cv2.addWeighted(overlay, 0.8, mask_colored, 0.2, 0)
        
    elif visualization_type == "bbox":
        # Bounding box visualization - encadre uniquement les zones d'anomalie
        overlay = img_uint8.copy()
        
        # Create binary mask with higher threshold for better precision
        binary_mask = (mask_resized > 0.5).astype(np.uint8)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours and draw bounding boxes only around anomaly regions
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and draw only significant anomaly regions
        min_area = 100
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw rectangle with thick red border
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), 3)
                
                # Add corner markers for better visibility
                corner_size = min(15, w // 4, h // 4)
                # Top-left corner
                cv2.line(overlay, (x, y), (x + corner_size, y), (255, 255, 0), 4)
                cv2.line(overlay, (x, y), (x, y + corner_size), (255, 255, 0), 4)
                # Top-right corner
                cv2.line(overlay, (x + w, y), (x + w - corner_size, y), (255, 255, 0), 4)
                cv2.line(overlay, (x + w, y), (x + w, y + corner_size), (255, 255, 0), 4)
                # Bottom-left corner
                cv2.line(overlay, (x, y + h), (x + corner_size, y + h), (255, 255, 0), 4)
                cv2.line(overlay, (x, y + h), (x, y + h - corner_size), (255, 255, 0), 4)
                # Bottom-right corner
                cv2.line(overlay, (x + w, y + h), (x + w - corner_size, y + h), (255, 255, 0), 4)
                cv2.line(overlay, (x + w, y + h), (x + w, y + h - corner_size), (255, 255, 0), 4)
                
                # Add semi-transparent red fill inside the box
                roi = overlay[y:y+h, x:x+w]
                red_overlay = np.full_like(roi, (255, 100, 100))
                overlay[y:y+h, x:x+w] = cv2.addWeighted(roi, 0.85, red_overlay, 0.15, 0)
                
    elif visualization_type == "circle":
        # Circle-based visualization
        overlay = img_uint8.copy()
        
        # Create binary mask
        binary_mask = (mask_resized > 0.5).astype(np.uint8)
        
        # Find contours and draw enclosing circles
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                # Find minimum enclosing circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                
                # Draw circle with thick red border
                cv2.circle(overlay, center, radius, (255, 0, 0), 3)
                # Add center point
                cv2.circle(overlay, center, 5, (255, 255, 0), -1)
                # Add crosshair
                cv2.line(overlay, (center[0] - 10, center[1]), (center[0] + 10, center[1]), (255, 255, 0), 2)
                cv2.line(overlay, (center[0], center[1] - 10), (center[0], center[1] + 10), (255, 255, 0), 2)
    
    else:
        # Fallback to medical visualization
        overlay = img_uint8.copy()
        binary_mask = (mask_resized > 0.65).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask_overlay = np.zeros_like(overlay)
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                cv2.fillPoly(mask_overlay, [contour], (255, 80, 80))
                cv2.drawContours(overlay, [contour], -1, (255, 0, 0), 2)
        overlay = cv2.addWeighted(overlay, 0.7, mask_overlay, 0.3, 0)

    # Encode to base64
    pil_img = Image.fromarray(overlay)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    b64_string = "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")
    
    # Retourner l'image ET le masque filtré
    # Si pas de masque filtré créé (autres méthodes de visualisation), utiliser le masque U-Net
    if final_filtered_mask is None:
        final_filtered_mask = (mask_resized > 0.5).astype(np.uint8) * 255
    
    return b64_string, final_filtered_mask


# ── Main prediction function ───────────────────────────────────────────────
def predict_skin_anomaly(
    image_path: str,
    classif_threshold: float = 0.5,
    anomaly_threshold: float = 0.5,
    seg_area_threshold: float = 0.02,
) -> dict:
    """
    Full pipeline: classify animal → detect anomaly → segment if anomaly.

    Returns a dict ready to be serialised as JSON by FastAPI.
    """
    # ── Load models (once) ────────────────────────────────────────────────
    try:
        _load_models()
    except Exception as e:
        return {"error": str(e)}

    # ── Preprocess ────────────────────────────────────────────────────────
    try:
        arr_exp, arr = _preprocess(image_path)
    except Exception as e:
        return {"error": f"Failed to read image: {e}"}

    # ══════════════════════════════════════════════════════════════════════
    # STEP 1 — CLASSIFICATION (Cat / Dog)
    # ══════════════════════════════════════════════════════════════════════
    proba_class = float(_classifier.predict(arr_exp, verbose=0)[0][0])
    classes_sorted = sorted(_class_indices, key=_class_indices.get)  # [class_0, class_1]

    if proba_class > classif_threshold:
        animal_key  = classes_sorted[1]
        animal_conf = proba_class
    else:
        animal_key  = classes_sorted[0]
        animal_conf = 1.0 - proba_class

    animal_info = ANIMAL_KB.get(animal_key.lower(), {"emoji": "🐾", "label": animal_key.capitalize()})

    # ══════════════════════════════════════════════════════════════════════
    # STEP 2 — ANOMALY DETECTION
    # ══════════════════════════════════════════════════════════════════════
    proba_anom = float(_anomaly_det.predict(arr_exp, verbose=0)[0][0])
    p_anomaly  = proba_anom if _anomaly_idx == 1 else 1.0 - proba_anom
    has_anomaly = p_anomaly > anomaly_threshold

    # ══════════════════════════════════════════════════════════════════════
    # STEP 3 — SEGMENTATION (only if anomaly detected)
    # ══════════════════════════════════════════════════════════════════════
    seg_overlay_b64 = None
    seg_area        = 0.0
    seg_confirmed   = False

    if has_anomaly:
        seg_mask_raw = _unet.predict(arr_exp, verbose=0)[0, :, :, 0]
        # Obtenir l'overlay ET le masque filtré
        seg_overlay_b64, filtered_mask = _mask_to_base64(seg_mask_raw, arr, "medical")
        # Calculer la zone affectée à partir du masque FILTRÉ (pas du masque U-Net brut)
        seg_pixels   = int(np.sum(filtered_mask > 0))
        seg_area     = seg_pixels / (IMG_SIZE[0] * IMG_SIZE[1])
        seg_confirmed = seg_area > seg_area_threshold

    # ══════════════════════════════════════════════════════════════════════
    # STEP 4 — FINAL DECISION
    # ══════════════════════════════════════════════════════════════════════
    final_anomaly  = has_anomaly or seg_confirmed
    combined_score = p_anomaly * 0.6 + seg_area * 0.4
    status_key     = "anomaly" if final_anomaly else "healthy"
    kb             = ANOMALY_KB[status_key]

    # Confidence for the anomaly/healthy verdict
    verdict_confidence = p_anomaly if final_anomaly else (1.0 - p_anomaly)

    return {
        # ── Animal classification ──────────────────────────────────────
        "animal": animal_key,
        "animal_label": animal_info["label"],
        "animal_emoji": animal_info["emoji"],
        "animal_confidence": round(animal_conf * 100, 1),

        # ── Anomaly detection ─────────────────────────────────────────
        "status": status_key,
        "status_label": kb["label"],
        "status_emoji": kb["emoji"],
        "status_description": kb["description"],
        "p_anomaly": round(p_anomaly * 100, 1),
        "p_healthy": round((1.0 - p_anomaly) * 100, 1),
        "verdict_confidence": round(verdict_confidence * 100, 1),

        # ── Segmentation ──────────────────────────────────────────────
        "segmentation_done": has_anomaly,
        "seg_area_pct": round(seg_area * 100, 2),
        "seg_overlay": seg_overlay_b64,   # base64 PNG or null

        # ── Knowledge base ────────────────────────────────────────────
        "cues": kb["cues"],
        "recommendation": kb["recommendation"],

        # ── Combined score ────────────────────────────────────────────
        "combined_score": round(combined_score * 100, 1),
    }
