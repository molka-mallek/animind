from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import deque
import os
import uuid

from modules.dog_emotion.ai_pipeline import predict_photo, predict_video
from modules.calf_behavior.ai_pipeline import predict_behavior

# ─────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# CALF CONFIG
# ─────────────────────────────────────────────
WINDOW_SIZE        = 100   # must match model_metadata.json
CONFIDENCE_THRESH  = 0.6   # below this → abnormal (low confidence)
INSTABILITY_WINDOW = 10    # last N predictions checked for instability
INSTABILITY_THRESH = 6     # if >6 unique behaviors in last 10 → unstable
EVENT_MIN_DURATION = 10    # consecutive predictions to declare an event

# ─────────────────────────────────────────────
# PER-CALF STATE
# ─────────────────────────────────────────────
# Each calf gets its own independent state dict
calf_states: dict[str, dict] = {}

def get_calf_state(calf_id: str) -> dict:
    """Return existing state or create a fresh one for a new calf."""
    if calf_id not in calf_states:
        calf_states[calf_id] = {
            "buffer":           deque(maxlen=WINDOW_SIZE),
            "recent_behaviors": deque(maxlen=INSTABILITY_WINDOW),
            "streak_behavior":  None,
            "streak_count":     0,
            "event_log":        [],   # list of {type, duration, behavior}
        }
    return calf_states[calf_id]

# ─────────────────────────────────────────────
# ABNORMAL DETECTION
# ─────────────────────────────────────────────
def detect_abnormal(behavior: str, confidence: float, recent: deque) -> dict:
    """
    Post-processing layer on top of model output.
    Returns alert info — does NOT override the raw model behavior.
    """
    if confidence < CONFIDENCE_THRESH:
        return {"alert": True, "alert_type": "low_confidence"}

    if len(recent) == INSTABILITY_WINDOW:
        unique_count = len(set(recent))
        if unique_count >= INSTABILITY_THRESH:
            return {"alert": True, "alert_type": "instability"}

    return {"alert": False, "alert_type": None}

# ─────────────────────────────────────────────
# EVENT DETECTION
# ─────────────────────────────────────────────
def detect_event(behavior: str, state: dict) -> dict:
    """
    Stateful event detection using streak tracking.
    Mutates state in place.
    """
    # update streak
    if behavior == state["streak_behavior"]:
        state["streak_count"] += 1
    else:
        state["streak_behavior"] = behavior
        state["streak_count"]    = 1

    streak = state["streak_count"]

    # activity spike: rapid switching (streak resets often → short streaks)
    recent = list(state["recent_behaviors"])
    if len(recent) >= INSTABILITY_WINDOW:
        unique = len(set(recent))
        if unique >= INSTABILITY_THRESH:
            return {"type": "activity_spike", "duration": streak}

    # sustained behavior events
    if streak >= EVENT_MIN_DURATION:
        if behavior in ("eating_drinking",):
            return {"type": "feeding_session", "duration": streak}
        if behavior in ("lying",):
            return {"type": "resting_session", "duration": streak}

    return {"type": "none", "duration": streak}

# ─────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "AniMind API is running"}

# ─────────────────────────────────────────────
# LIST ACTIVE CALVES
# ─────────────────────────────────────────────
@app.get("/calves")
def list_calves():
    return {"calves": list(calf_states.keys())}

# ─────────────────────────────────────────────
# DOG IMAGE
# ─────────────────────────────────────────────
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    temp_path = None
    try:
        contents  = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(contents)
        return predict_photo(temp_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ─────────────────────────────────────────────
# DOG VIDEO
# ─────────────────────────────────────────────
@app.post("/predict-video")
async def predict_video_api(file: UploadFile = File(...)):
    temp_path = None
    try:
        contents  = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.mp4"
        with open(temp_path, "wb") as f:
            f.write(contents)
        return predict_video(temp_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ─────────────────────────────────────────────
# CALF PREDICTION (MULTI-CALF)
# ─────────────────────────────────────────────
class CalfInput(BaseModel):
    id:   str   = "calf_1"   # calf identifier — defaults to calf_1
    accX: float
    accY: float
    accZ: float

@app.post("/predict-calf")
async def predict_calf(data: CalfInput):
    try:
        state = get_calf_state(data.id)

        # 1. Add reading to this calf's buffer
        state["buffer"].append([data.accX, data.accY, data.accZ])

        if len(state["buffer"]) < WINDOW_SIZE:
            return {
                "status":   "warming_up",
                "calf_id":  data.id,
                "progress": len(state["buffer"]),
                "required": WINDOW_SIZE,
            }

        # 2. Run model inference
        result = predict_behavior(list(state["buffer"]))
        behavior   = result["behavior"]
        confidence = result["confidence"]

        # 3. Update recent behavior history
        state["recent_behaviors"].append(behavior)

        # 4. Abnormal detection layer
        abnormal = detect_abnormal(behavior, confidence, state["recent_behaviors"])

        # 5. Event detection
        event = detect_event(behavior, state)

        # 6. Log significant events (avoid duplicates)
        if event["type"] != "none":
            last = state["event_log"][-1] if state["event_log"] else None
            if not last or last["type"] != event["type"]:
                state["event_log"].append(event)
                if len(state["event_log"]) > 50:   # cap log size
                    state["event_log"].pop(0)

        return {
            "status":  "success",
            "calf_id": data.id,
            "result":  {
                **result,
                "alert":      abnormal["alert"],
                "alert_type": abnormal["alert_type"],
                "event":      event,
            },
        }

    except Exception as e:
        return {"status": "error", "calf_id": data.id, "message": str(e)}
