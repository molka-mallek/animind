from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid

from modules.dog_emotion.ai_pipeline import predict_photo, predict_video

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