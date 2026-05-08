from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import deque
import os
import uuid
import importlib.util
from pathlib import Path

# ─────────────────────────────────────────────
# LAZY LOADING FOR ALL PIPELINES
# ─────────────────────────────────────────────
predict_photo = None
predict_video = None
_dog_pipeline_error = None
predict_behavior = None
_calf_pipeline_error = None
predict_eye_infection = None
_eye_pipeline_error = None
predict_fowlpox = None
_fowlpox_pipeline_error = None
predict_bird_droppings = None
_bird_droppings_pipeline_error = None
predict_skin_anomaly = None
_skin_anomaly_pipeline_error = None


def _ensure_dog_pipeline_loaded():
    global predict_photo, predict_video, _dog_pipeline_error
    if predict_photo is not None and predict_video is not None:
        return None
    if _dog_pipeline_error is not None:
        return _dog_pipeline_error
    try:
        from modules.dog_emotion.ai_pipeline import predict_photo as _predict_photo, predict_video as _predict_video
        predict_photo = _predict_photo
        predict_video = _predict_video
        return None
    except Exception as e:
        _dog_pipeline_error = str(e)
        return _dog_pipeline_error


def _ensure_calf_pipeline_loaded():
    global predict_behavior, _calf_pipeline_error
    if predict_behavior is not None:
        return None
    if _calf_pipeline_error is not None:
        return _calf_pipeline_error
    try:
        from modules.calf_behavior.ai_pipeline import predict_behavior as _predict_behavior
        predict_behavior = _predict_behavior
        return None
    except Exception as e:
        _calf_pipeline_error = str(e)
        return _calf_pipeline_error


def _load_function_from_file(path: Path, module_name: str, function_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None, f"Failed to load module from {path}"
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        return None, str(e)
    func = getattr(module, function_name, None)
    if func is None:
        return None, f"Function {function_name} not found in {path}"
    return func, None


def _ensure_eye_pipeline_loaded():
    global predict_eye_infection, _eye_pipeline_error
    if predict_eye_infection is not None:
        return None
    if _eye_pipeline_error is not None:
        return _eye_pipeline_error
    pipeline_path = (
        Path(__file__).resolve().parent
        / "modules"
        / "cat and dogs eye infection"
        / "ai_pipeline.py"
    )
    func, err = _load_function_from_file(
        pipeline_path,
        "cat_dog_eye_infection_pipeline",
        "predict_eye_infection",
    )
    if err:
        _eye_pipeline_error = err
        return err
    predict_eye_infection = func
    return None


def _ensure_fowlpox_pipeline_loaded():
    global predict_fowlpox, _fowlpox_pipeline_error
    if predict_fowlpox is not None:
        return None
    if _fowlpox_pipeline_error is not None:
        return _fowlpox_pipeline_error
    pipeline_path = (
        Path(__file__).resolve().parent
        / "modules"
        / "chiken"
        / "fowlpox_ai_pipeline.py"
    )
    func, err = _load_function_from_file(
        pipeline_path,
        "chicken_fowlpox_pipeline",
        "predict_fowlpox",
    )
    if err:
        _fowlpox_pipeline_error = err
        return err
    predict_fowlpox = func
    return None


def _ensure_bird_droppings_pipeline_loaded():
    global predict_bird_droppings, _bird_droppings_pipeline_error
    if predict_bird_droppings is not None:
        return None
    if _bird_droppings_pipeline_error is not None:
        return _bird_droppings_pipeline_error
    pipeline_path = (
        Path(__file__).resolve().parent
        / "modules"
        / "chiken"
        / "bird_droppings_ai_pipeline.py"
    )
    func, err = _load_function_from_file(
        pipeline_path,
        "bird_droppings_pipeline",
        "predict_bird_droppings",
    )
    if err:
        _bird_droppings_pipeline_error = err
        return err
    predict_bird_droppings = func
    return None


def _ensure_skin_anomaly_pipeline_loaded():
    global predict_skin_anomaly, _skin_anomaly_pipeline_error
    if predict_skin_anomaly is not None:
        return None
    if _skin_anomaly_pipeline_error is not None:
        return _skin_anomaly_pipeline_error
    pipeline_path = (
        Path(__file__).resolve().parent
        / "modules"
        / "skin_anomaly"
        / "ai_pipeline.py"
    )
    func, err = _load_function_from_file(
        pipeline_path,
        "skin_anomaly_pipeline",
        "predict_skin_anomaly",
    )
    if err:
        _skin_anomaly_pipeline_error = err
        return err
    predict_skin_anomaly = func
    return None

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
        dog_error = _ensure_dog_pipeline_loaded()
        if dog_error:
            return {"error": f"Dog emotion model unavailable: {dog_error}"}

        contents = await file.read()
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
        dog_error = _ensure_dog_pipeline_loaded()
        if dog_error:
            return {"error": f"Dog emotion model unavailable: {dog_error}"}

        contents = await file.read()
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
        calf_error = _ensure_calf_pipeline_loaded()
        if calf_error:
            return {"error": f"Calf behavior model unavailable: {calf_error}"}

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

# ─────────────────────────────────────────────
# EYE INFECTION PREDICTION
# ─────────────────────────────────────────────
@app.post("/predict-eye-infection")
async def predict_eye_infection_api(file: UploadFile = File(...)):
    temp_path = None
    try:
        eye_error = _ensure_eye_pipeline_loaded()
        if eye_error:
            return {"error": f"Eye infection model unavailable: {eye_error}"}

        contents = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(contents)
        result = predict_eye_infection(temp_path)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ─────────────────────────────────────────────
# CHICKEN FOWLPOX PREDICTION
# ─────────────────────────────────────────────
@app.post("/predict-chicken-fowlpox")
async def predict_chicken_fowlpox_api(file: UploadFile = File(...)):
    temp_path = None
    try:
        fowlpox_error = _ensure_fowlpox_pipeline_loaded()
        if fowlpox_error:
            return {"error": f"Chicken fowlpox model unavailable: {fowlpox_error}"}

        contents = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(contents)
        result = predict_fowlpox(temp_path)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ─────────────────────────────────────────────
# BIRD DROPPINGS PREDICTION
# ─────────────────────────────────────────────
@app.post("/predict-bird-droppings")
async def predict_bird_droppings_api(file: UploadFile = File(...)):
    temp_path = None
    try:
        droppings_error = _ensure_bird_droppings_pipeline_loaded()
        if droppings_error:
            return {"error": f"Bird droppings model unavailable: {droppings_error}"}

        contents = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(contents)
        result = predict_bird_droppings(temp_path)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ── SKIN ANOMALY PREDICTION ────────────────────
@app.post("/predict-skin-anomaly")
async def predict_skin_anomaly_api(file: UploadFile = File(...)):
    temp_path = None

    try:
        skin_error = _ensure_skin_anomaly_pipeline_loaded()
        if skin_error:
            return {"error": f"Skin anomaly model unavailable: {skin_error}"}

        contents = await file.read()
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"

        with open(temp_path, "wb") as f:
            f.write(contents)

        result = predict_skin_anomaly(temp_path)
        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
