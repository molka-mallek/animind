import tensorflow as tf
import numpy as np
import cv2
from ultralytics import YOLO
from collections import deque, Counter
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ─────────────────────────────────────────
IMG_SIZE = 224
CLASSES = ['alert', 'angry', 'frown', 'happy', 'relax']

# ── LOAD MODEL ─────────────────────────────────────
model = tf.keras.models.load_model("model/dog_emotion_best_model.keras")

# ── YOLO (lazy load) ───────────────────────────────
YOLO_MODEL = None

def get_yolo():
    global YOLO_MODEL
    if YOLO_MODEL is None:
        YOLO_MODEL = YOLO("yolov8n.pt")
    return YOLO_MODEL


# ── DETECT DOG ─────────────────────────────────────
def detect_and_crop_dog(frame_bgr):
    yolo = get_yolo()
    results = yolo(frame_bgr, classes=[16], verbose=False)

    boxes = []
    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 16:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                boxes.append((x1, y1, x2, y2))

    if not boxes:
        return None

    x1, y1, x2, y2 = max(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
    return frame_bgr[y1:y2, x1:x2]


# ── TEMPORAL SMOOTHING ─────────────────────────────
class TemporalSmoother:
    def __init__(self, window=5):
        self.buffer = deque(maxlen=window)

    def update(self, probs):
        self.buffer.append(probs)
        return np.mean(self.buffer, axis=0)


# ── KNOWLEDGE BASE ─────────────────────────────────
EMOTION_KB = {
    'angry': {
        'cues': ["Ears pinned back or flat", "Wrinkled muzzle / exposed teeth",
                 "Hard, fixed stare", "Tense facial muscles", "Body leaning forward"],
        'body': "Stiff, forward-leaning posture signals threat readiness.",
        'advice': "Give the dog space. Remove the stressor. Avoid direct eye contact.",
        'emoji': "😤",
    },
    'frown': {
        'cues': ["Furrowed brow", "Ears slightly pulled back",
                 "Downcast eyes", "Drooping mouth"],
        'body': "Subtle signs of discomfort or stress.",
        'advice': "Check for discomfort and provide reassurance.",
        'emoji': "😟",
    },
    'alert': {
        'cues': ["Ears forward", "Eyes wide open",
                 "Head raised", "Sniffing"],
        'body': "Dog is attentive and focused.",
        'advice': "Allow safe exploration.",
        'emoji': "👀",
    },
    'happy': {
        'cues': ["Soft eyes", "Relaxed mouth",
                 "Loose body", "Natural ears"],
        'body': "Dog is relaxed and content.",
        'advice': "Great time for bonding.",
        'emoji': "😄",
    },
    'relax': {
        'cues': ["Half-closed eyes", "Loose ears",
                 "Soft mouth", "Low tension"],
        'body': "Dog feels safe and calm.",
        'advice': "Maintain this calm environment.",
        'emoji': "😌",
    },
}


# ── IMAGE PREDICTION ───────────────────────────────
def predict_photo(image_path):

    bgr = cv2.imread(image_path)
    if bgr is None:
        return {"error": "Failed to read image"}

    crop = detect_and_crop_dog(bgr)
    if crop is None:
        crop = bgr

    img = cv2.resize(crop, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    probs = model.predict(img)[0]
    pred_idx = int(np.argmax(probs))

    emotion = CLASSES[pred_idx]
    confidence = float(probs[pred_idx])
    kb = EMOTION_KB.get(emotion)

    return {
        "emotion": emotion,
        "confidence": confidence,
        "emoji": kb["emoji"],
        "cues": kb["cues"],
        "body": kb["body"],
        "advice": kb["advice"]
    }


# ── VIDEO PREDICTION (FINAL CLEAN) ─────────────────
def predict_video(video_path, sample_every_n=8):

    cap = cv2.VideoCapture(video_path)
    smoother = TemporalSmoother()

    frame_count = 0
    smoothed_emotions = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % sample_every_n == 0:

            crop = detect_and_crop_dog(frame)
            if crop is None:
                crop = frame

            img = cv2.resize(crop, (IMG_SIZE, IMG_SIZE))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            probs = model.predict(img)[0]

            smoothed_probs = smoother.update(probs)
            pred_idx = int(np.argmax(smoothed_probs))
            emotion = CLASSES[pred_idx]

            smoothed_emotions.append(emotion)

        frame_count += 1

    cap.release()

    if not smoothed_emotions:
        return {"error": "No frames processed"}

    final_emotion = max(set(smoothed_emotions), key=smoothed_emotions.count)
    confidence = smoothed_emotions.count(final_emotion) / len(smoothed_emotions)

    kb = EMOTION_KB.get(final_emotion)

    # 🔥 FIXED EVOLUTION LOGIC
    counts = Counter(smoothed_emotions)
    most_common = counts.most_common()

    if len(most_common) == 1:
        evolution = "The dog's behavior remained stable throughout the video."
    else:
        main_emotion = most_common[0][0]
        secondary_emotion = most_common[1][0]

        if main_emotion == secondary_emotion:
            evolution = "The dog's behavior remained stable throughout the video."
        else:
            evolution = f"The dog's behavior showed slight variations but remained mostly {main_emotion}."

    return {
        "emotion": final_emotion,
        "confidence": confidence,
        "emoji": kb["emoji"],
        "cues": kb["cues"],
        "body": kb["body"],
        "advice": kb["advice"],
        "evolution": evolution
    }