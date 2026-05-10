"""
Cat Sound Classification — YAMNet + head network pipeline for AniMind
Classifies cat vocalizations into 10 behavioral categories.
"""
from pathlib import Path
import warnings
import json
import numpy as np

warnings.filterwarnings("ignore")

MODEL_DIR = Path(__file__).resolve().parents[3] / "model" / "cat_sound"

# ── Metadata ─────────────────────────────────────────────────
with open(MODEL_DIR / "metadata.json") as f:
    META = json.load(f)

CLASS_NAMES = META["class_names"]       # 10 classes
CLASS_TIER  = META["class_tier"]        # clinical priority tier
TIER_COLORS = META["tier_colors"]
TIER_ALERT  = {1: "critical", 2: "warning", 3: "normal", 4: "info"}

RECOMMENDATIONS = {
    "Paining":     "Your cat may be in pain. Please consult a veterinarian immediately.",
    "Defence":     "Your cat feels threatened. Give it space and identify the stressor.",
    "Fighting":    "Your cat is in aggressive conflict. Separate animals and check for injuries.",
    "Warning":     "Your cat is issuing a warning. Approach carefully and remove stressors.",
    "Angry":       "Your cat is expressing anger. Avoid interaction until calmer.",
    "Happy":       "Your cat sounds content and happy!",
    "Resting":     "Your cat is calm and resting.",
    "MotherCall":  "Maternal calling detected — normal if nursing kittens.",
    "HuntingMind": "Your cat is in hunting mode — normal predatory behavior.",
    "Mating":      "Mating call detected. Consider spaying/neutering if not planned.",
}

# ── Singleton load ───────────────────────────────────────────
_yamnet = None
_head   = None


def _load():
    global _yamnet, _head
    if _head is not None:
        return

    import tensorflow_hub as hub
    import tf_keras as tfk
    import h5py

    _yamnet = hub.load("https://tfhub.dev/google/yamnet/1")

    # Rebuild head model (Keras 3 format ↔ tf_keras incompatibility workaround)
    inp = tfk.Input(shape=(1024,), name="yamnet_embedding")
    x   = tfk.layers.Dense(512, activation="relu",    name="dense_6")(inp)
    x   = tfk.layers.Dropout(0.3,                     name="dropout_4")(x)
    x   = tfk.layers.Dense(256, activation="relu",    name="dense_7")(x)
    x   = tfk.layers.Dropout(0.3,                     name="dropout_5")(x)
    out = tfk.layers.Dense(10,  activation="softmax", name="dense_8")(x)
    model = tfk.Model(inputs=inp, outputs=out, name="yamnet_head")

    # Load weights directly via h5py (avoids tf_keras/Keras-3 format conflict)
    weights_path = MODEL_DIR / "head_model.weights.h5"
    with h5py.File(str(weights_path), "r") as h5:
        dense_keys   = ["dense", "dense_1", "dense_2"]
        dense_layers = [L for L in model.layers if L.__class__.__name__ == "Dense"]
        for layer, key in zip(dense_layers, dense_keys):
            layer.set_weights([
                h5[f"layers/{key}/vars/0"][:],
                h5[f"layers/{key}/vars/1"][:],
            ])
    _head = model


# ── Public API ───────────────────────────────────────────────
def predict_cat_sound(audio_path: str) -> dict:
    import tensorflow as tf
    import librosa

    _load()

    # Load & normalise audio to 16 kHz mono, 2 s
    waveform, _ = librosa.load(audio_path, sr=16000, mono=True)
    target      = META.get("target_samples", 32000)
    if len(waveform) < target:
        waveform = np.pad(waveform, (0, target - len(waveform)))
    else:
        waveform = waveform[:target]

    wav_tensor = tf.constant(waveform, dtype=tf.float32)

    # YAMNet embedding
    _, embeddings, _ = _yamnet(wav_tensor)
    embedding        = tf.reduce_mean(embeddings, axis=0, keepdims=True)

    # Head model
    probs      = _head(embedding, training=False).numpy()[0]
    pred_idx   = int(np.argmax(probs))
    class_name = CLASS_NAMES[pred_idx]
    confidence = float(probs[pred_idx])
    tier       = CLASS_TIER.get(class_name, 4)
    alert      = TIER_ALERT.get(tier, "info")
    color      = TIER_COLORS.get(str(tier), "#7f7f7f")

    # Top-3
    top3_idx = np.argsort(probs)[::-1][:3]
    top3 = [{"class": CLASS_NAMES[i], "probability": float(probs[i])} for i in top3_idx]

    return {
        "prediction":        class_name,
        "confidence":        confidence,
        "tier":              tier,
        "alert_level":       alert,
        "color":             color,
        "top3":              top3,
        "all_probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))},
        "emoji":             "🔴" if tier == 1 else "🟠" if tier == 2 else "🟢" if tier == 3 else "⚪",
        "recommendation":    RECOMMENDATIONS.get(class_name, ""),
    }
