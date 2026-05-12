"""
Cat Vocalization Classification — AI Pipeline
Runs in the main backend venv (tensorflow>=2.20 + tensorflow-hub + librosa required)
Compatible with Python 3.12/3.13 + TensorFlow 2.20+
"""
import os
import json
import numpy as np

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR    = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "model", "cat_sound")
HEAD_MODEL   = os.path.join(MODEL_DIR, "head_model.keras")
HEAD_WEIGHTS = os.path.join(MODEL_DIR, "model.weights.h5")  # extracted from .keras zip
METADATA     = os.path.join(MODEL_DIR, "metadata.json")
YAMNET_CACHE = os.path.join(MODEL_DIR, "yamnet_cache")

# ── Load metadata ──────────────────────────────────────────────────────────
with open(METADATA) as f:
    _meta = json.load(f)

CLASS_NAMES    = _meta["class_names"]
CLASS_TIER     = _meta["class_tier"]
PAIN_THRESHOLD = _meta["pain_threshold"]
TARGET_SR      = _meta["target_sr"]
TARGET_SAMPLES = _meta["target_samples"]
TIER_COLORS    = _meta["tier_colors"]

TIER_ICONS = {"1": "🔴", "2": "🟠", "3": "🟢", "4": "⚪"}

VOCALIZATION_INFO = {
    "Angry":       {"desc": "Cat is expressing aggression or irritation.", "advice": "Remove the stressor. Give the cat space and avoid direct contact."},
    "Defence":     {"desc": "Cat feels threatened and is in a defensive posture.", "advice": "Identify and remove the perceived threat. Provide a safe hiding spot."},
    "Fighting":    {"desc": "Cat is engaged in or anticipating a fight.", "advice": "Separate cats immediately. Check for injuries and consult a vet if needed."},
    "Happy":       {"desc": "Cat is content and expressing positive emotions.", "advice": "Great time for bonding and play. Maintain this positive environment."},
    "HuntingMind": {"desc": "Cat is in a focused hunting or stalking mindset.", "advice": "Provide interactive toys to channel this natural instinct safely."},
    "Mating":      {"desc": "Cat is vocalizing for mating purposes.", "advice": "Consider spaying/neutering to reduce stress and unwanted behaviors."},
    "MotherCall":  {"desc": "Mother cat communicating with kittens.", "advice": "Ensure a quiet, safe nesting area. Minimize disturbances."},
    "Paining":     {"desc": "Cat is vocalizing due to pain or severe distress.", "advice": "🚨 Seek veterinary attention immediately. This is a clinical priority."},
    "Resting":     {"desc": "Cat is relaxed and at ease.", "advice": "Maintain this calm environment. Ensure comfort and warmth."},
    "Warning":     {"desc": "Cat is issuing a warning signal to a perceived threat.", "advice": "Identify the trigger. Give the cat space and reduce stressors."},
}

# ── Lazy-loaded models ─────────────────────────────────────────────────────
_yamnet = None
_head   = None


def _load_models():
    global _yamnet, _head
    if _yamnet is not None and _head is not None:
        return

    import tensorflow_hub as hub
    import h5py

    try:
        import tf_keras as keras
    except ImportError:
        import keras

    os.environ.setdefault("TFHUB_CACHE_DIR", YAMNET_CACHE)
    _yamnet = hub.load("https://tfhub.dev/google/yamnet/1")

    # Build exact architecture from config.json inside the .keras file
    inp   = keras.Input(shape=(1024,), name="yamnet_embedding")
    x     = keras.layers.Dense(512, activation="relu",    name="dense_6")(inp)
    x     = keras.layers.Dropout(0.3,                     name="dropout_4")(x)
    x     = keras.layers.Dense(256, activation="relu",    name="dense_7")(x)
    x     = keras.layers.Dropout(0.3,                     name="dropout_5")(x)
    out   = keras.layers.Dense(10,  activation="softmax", name="dense_8")(x)
    _head = keras.Model(inp, out, name="yamnet_head")

    # Load weights manually from Keras 3 h5 format
    # Keys: layers/dense/vars/0 (kernel), layers/dense/vars/1 (bias)
    with h5py.File(HEAD_WEIGHTS, "r") as f:
        dense_layers = [l for l in _head.layers if isinstance(l, keras.layers.Dense)]
        h5_keys      = ["dense", "dense_1", "dense_2"]
        for layer, key in zip(dense_layers, h5_keys):
            kernel = f[f"layers/{key}/vars/0"][:]
            bias   = f[f"layers/{key}/vars/1"][:]
            layer.set_weights([kernel, bias])


def _preprocess(path: str) -> "np.ndarray":
    import librosa
    y, _ = librosa.load(path, sr=TARGET_SR, mono=True)
    if len(y) < TARGET_SAMPLES:
        pad = TARGET_SAMPLES - len(y)
        y = np.pad(y, (pad // 2, pad - pad // 2), mode="reflect")
    else:
        start = (len(y) - TARGET_SAMPLES) // 2
        y = y[start: start + TARGET_SAMPLES]
    peak = np.abs(y).max()
    if peak > 0:
        y = y / peak
    return y.astype(np.float32)


def predict_cat_sound(audio_path: str) -> dict:
    import tensorflow as tf

    _load_models()
    wav       = _preprocess(audio_path)
    _, emb, _ = _yamnet(wav)
    emb_pool  = tf.reduce_mean(emb, axis=0, keepdims=True)
    proba     = _head(emb_pool, training=False).numpy()[0]

    pred_idx    = int(np.argmax(proba))
    pred_label  = CLASS_NAMES[pred_idx]
    confidence  = float(proba[pred_idx])
    pain_prob   = float(proba[CLASS_NAMES.index("Paining")])
    pain_alert  = pain_prob >= PAIN_THRESHOLD

    tier_key    = str(CLASS_TIER[pred_label])
    info        = VOCALIZATION_INFO.get(pred_label, {})

    # Build sorted probability list
    all_probs = []
    for i, name in enumerate(CLASS_NAMES):
        t = str(CLASS_TIER[name])
        all_probs.append({
            "class":      name,
            "probability": round(float(proba[i]) * 100, 1),
            "tier":        int(t),
            "tier_icon":   TIER_ICONS[t],
            "tier_color":  TIER_COLORS[t],
        })
    all_probs.sort(key=lambda x: x["probability"], reverse=True)

    return {
        "predicted_class":  pred_label,
        "confidence":       round(confidence * 100, 1),
        "tier":             int(tier_key),
        "tier_icon":        TIER_ICONS[tier_key],
        "pain_alert":       pain_alert,
        "pain_probability": round(pain_prob * 100, 1),
        "pain_threshold":   round(PAIN_THRESHOLD * 100, 1),
        "description":      info.get("desc", ""),
        "advice":           info.get("advice", ""),
        "all_probabilities": all_probs,
    }