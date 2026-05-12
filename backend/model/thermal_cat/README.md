# Thermal Cat Classification — Model Files

These files are **not included in the repository** (too large for git).
Download the zip below, extract it, and place the files in this folder.

---

## Download

📦 **[Download thermal_cat_models.zip](https://drive.google.com/drive/folders/1nUy1rBTOi13bzhY1RVOKvr8RTSMKiTTy?usp=drive_link)** (~145 MB)

---

## After downloading

1. Extract the zip
2. Place all 3 files in `backend/model/thermal_cat/`:

```
backend/model/thermal_cat/
├── custom_cnn.pth          ← from zip
├── efficientnet_b3.pth     ← from zip
├── resnet50.pth            ← from zip
└── inference_config.json   ← already in repo ✅
```

3. Do **not** replace `inference_config.json` — it's already there.

---

## Dependencies

Already included in `requirements.txt` — no extra installs needed:

```
torch>=2.2.0
torchvision>=0.17.0
pillow>=10.2.0
numpy>=1.26.0
```

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

Classifies thermal cat images as **Healthy** or **Sick** using an ensemble of 3 models:
- `custom_cnn.pth` — Custom CNN (weight: 20%)
- `efficientnet_b3.pth` — EfficientNet-B3 (weight: 50%)
- `resnet50.pth` — ResNet50 (weight: 30%)

- Classification threshold: **56%** sick probability
- Optimized for **high recall** (minimizes false negatives)
- Accepts **PNG, JPG, WEBP** thermal images (RGB, not grayscale)
- Runs fully offline — no internet required after model placement