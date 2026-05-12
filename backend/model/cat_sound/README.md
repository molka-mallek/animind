# Cat Vocalization Classification — Model Files

These files are **not included in the repository** (too large for git).
Download the zip below, extract it, and place the files in this folder.

---

## Download

📦 **[Download cat_sound_model.zip](https://drive.google.com/drive/folders/1BIneQCrTTO99OFL1hLAdruFjTLKxlZxh)** (~7.6 MB)

---

## After downloading

1. Extract the zip
2. Place `head_model.keras` in `backend/model/cat_sound/` so it looks like this:

```
backend/model/cat_sound/
├── head_model.keras      ← from zip
├── metadata.json         ← already in repo ✅
└── yamnet_cache/         ← created automatically on first run ✅
```

3. Extract the internal weights file from the `.keras` archive (required once):

```cmd
cd backend
venv\Scripts\python.exe -c "
import zipfile
with zipfile.ZipFile('model/cat_sound/head_model.keras', 'r') as z:
    z.extract('model.weights.h5', 'model/cat_sound/')
print('Done')
"
```

This creates `model/cat_sound/model.weights.h5` which the pipeline uses to load weights correctly on TF 2.20+.

---

## Dependencies

Install after `pip install -r requirements.txt`:

```cmd
pip install tensorflow>=2.20.0 tensorflow-hub>=0.16.0 tf-keras>=2.20.0
```

> `librosa` and `soundfile` are already included in `requirements.txt`.

---

## How to start the backend

⚠️ Always use this command — **not** plain `uvicorn`:

```cmd
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Or use the provided script:

```cmd
cd backend
start.bat
```

---

## What this model does

Classifies cat vocalizations into **10 behavioral categories**:
`Angry`, `Defence`, `Fighting`, `Happy`, `HuntingMind`, `Mating`, `MotherCall`, `Paining`, `Resting`, `Warning`

- Triggers a **pain alert** when `Paining` probability exceeds 35%
- Uses **YAMNet** (Google audio embedding) + custom head classifier
- Architecture: `Dense(512) → Dropout → Dense(256) → Dropout → Dense(10, softmax)`
- Accepts **MP3 / WAV** audio files (1–3 seconds ideal)
- YAMNet cache (~25 MB) is downloaded automatically on first run