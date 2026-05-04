from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import importlib.util
from pathlib import Path

predict_photo = None
predict_video = None
_dog_pipeline_error = None
predict_eye_infection = None
_eye_pipeline_error = None
predict_fowlpox = None
_fowlpox_pipeline_error = None
predict_bird_droppings = None
_bird_droppings_pipeline_error = None


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

# ── INIT APP ───────────────────────────────────────
app = FastAPI()

# ── CORS ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROOT ───────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "AniMind API is running"}


# ── IMAGE PREDICTION ───────────────────────────────
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    temp_path = None

    try:
        dog_error = _ensure_dog_pipeline_loaded()
        if dog_error:
            return {"error": f"Dog emotion model unavailable: {dog_error}"}

        contents = await file.read()

        # 🔥 unique temp file (avoids conflicts)
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"

        with open(temp_path, "wb") as f:
            f.write(contents)

        result = predict_photo(temp_path)
        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        # 🔥 always clean file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ── VIDEO PREDICTION ───────────────────────────────
@app.post("/predict-video")
async def predict_video_api(file: UploadFile = File(...)):
    temp_path = None

    try:
        dog_error = _ensure_dog_pipeline_loaded()
        if dog_error:
            return {"error": f"Dog emotion model unavailable: {dog_error}"}

        contents = await file.read()

        # 🔥 unique temp file
        temp_path = f"temp_{uuid.uuid4().hex}.mp4"

        with open(temp_path, "wb") as f:
            f.write(contents)

        result = predict_video(temp_path)
        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        # 🔥 always clean file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ── EYE INFECTION PREDICTION ────────────────────
@app.post("/predict-eye-infection")
async def predict_eye_infection_api(file: UploadFile = File(...)):
    temp_path = None

    try:
        eye_error = _ensure_eye_pipeline_loaded()
        if eye_error:
            return {"error": f"Eye infection model unavailable: {eye_error}"}

        contents = await file.read()

        # 🔥 unique temp file
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"

        with open(temp_path, "wb") as f:
            f.write(contents)

        result = predict_eye_infection(temp_path)
        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        # 🔥 always clean file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ── CHICKEN FOWLPOX PREDICTION ────────────────────
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


# ── BIRD DROPPINGS PREDICTION ────────────────────
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
