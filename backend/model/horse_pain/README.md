# Horse Pain Detection — Model Files

These files are **not included in the repository** (binary model files).
Download the zip below, extract it, and place the files in this folder.

---

## Download

📦 **[Download horse_pain_models.zip](https://drive.google.com/drive/folders/1oRmKHZnCMFUJ1lXBcLG6BpRCrUvaronf?usp=sharing)** (~0.6 MB)

---

## After downloading

1. Extract the zip
2. Place all 3 files in `backend/model/horse_pain/`:

```
backend/model/horse_pain/
├── behavior_bilstm.pt    ← from zip
├── train_mean.npy        ← from zip
└── train_std.npy         ← from zip
```

---

## Dependencies

Install **in order** after `pip install -r requirements.txt`:

```cmd
pip install scikit-image filterpy ffmpeg-python onnxruntime
pip install git+https://github.com/JunkyByte/easy_ViTPose.git
```

> `torch`, `torchvision`, `opencv-python`, `huggingface_hub` are already in `requirements.txt`.

ViTPose weights (~360 MB) are downloaded automatically from HuggingFace on the **first inference run** and cached locally. This takes 1–3 minutes on first use.

---

## How to start the backend

⚠️ Always use this command — **not** plain `uvicorn`:

```cmd
cd backend
set HF_TOKEN=your_huggingface_token_here
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Or use the provided script (token already set inside):

```cmd
cd backend
start.bat
```

Using plain `uvicorn` picks up the system Python instead of the venv, causing `No module named 'easy_ViTPose'` errors.

---

## What this model does

Detects **pain and distress** in horses from video using:
1. **YOLO** — detects horse bounding box per frame
2. **ViTPose** — extracts 17 body keypoints from the cropped region
3. **Feature extraction** — 42 biomechanical features per frame (34 normalized coords + 4 joint angles + 4 symmetry ratios)
4. **BiLSTM + Attention** — classifies sequence as `normal` or `distress`

Outputs: `No Pain` or `Pain Detected` with confidence score.
Accepts **MP4, MOV, AVI** video files.