import numpy as np
import pickle
import json
import tensorflow as tf

# ── LOAD MODEL ─────────────────────────────────────────
BASE_PATH = "model/calf_behavior/"

model = tf.keras.models.load_model(
    BASE_PATH + "model.keras",
    compile=False
)

scaler = pickle.load(open(BASE_PATH + "scaler.pkl", "rb"))
label_encoder = pickle.load(open(BASE_PATH + "label_encoder.pkl", "rb"))

with open(BASE_PATH + "model_metadata.json") as f:
    meta = json.load(f)

CLASS_NAMES = meta["class_names"]


# ── FEATURE ENGINEERING ────────────────────────────────
def engineer_features(accX, accY, accZ):

    accX = np.array(accX)
    accY = np.array(accY)
    accZ = np.array(accZ)

    # magnitude
    mag = np.sqrt(accX**2 + accY**2 + accZ**2)

    # static component
    sX, sY, sZ = accX.mean(), accY.mean(), accZ.mean()

    # dynamic component
    dX, dY, dZ = accX - sX, accY - sY, accZ - sZ

    # activity metrics
    ODBA  = np.abs(dX) + np.abs(dY) + np.abs(dZ)
    VeDBA = np.sqrt(dX**2 + dY**2 + dZ**2)

    # orientation
    pitch = np.full(len(accX),
                    np.degrees(np.arctan2(sX, np.sqrt(sY**2 + sZ**2))))

    roll = np.full(len(accX),
                   np.degrees(np.arctan2(sY, sZ)))

    features = np.stack(
        [accX, accY, accZ, mag, ODBA, VeDBA, pitch, roll],
        axis=1
    )

    # scale
    features = scaler.transform(features).astype(np.float32)

    return features  # (50, 8)


# ── PREDICTION FUNCTION ────────────────────────────────
def predict_behavior(window):

    window = np.array(window)  # (50, 3)

    accX = window[:, 0]
    accY = window[:, 1]
    accZ = window[:, 2]

    # feature engineering → (50, 8)
    features = engineer_features(accX, accY, accZ)

    # reshape for model → (1, 50, 8)
    features = np.expand_dims(features, axis=0)

    # prediction
    probs = model.predict(features, verbose=0)[0]

    idx = int(np.argmax(probs))
    label = CLASS_NAMES[idx]
    confidence = float(probs[idx])

    return {
        "behavior": label,
        "confidence": round(confidence, 4),
        "probabilities": {
            CLASS_NAMES[i]: round(float(probs[i]), 4)
            for i in range(len(CLASS_NAMES))
        }
    }