# Thermal Cat Classification — Model Files

These files are **not included in the repository** (too large for git).
Download the zip below, extract it, and place the files in this folder.

---

## Download

📦 **[Download thermal_cat_models.zip](https://drive.google.com/drive/folders/1nUy1rBTOi13bzhY1RVOKvr8RTSMKiTTy?usp=drive_link)** (~145 MB)

---

## After downloading

1. Extract the zip
2. Place all 3 files in `backend/model/thermal_cat/` so it looks like this:

```
backend/model/thermal_cat/
├── custom_cnn.pth          ← from zip
├── efficientnet_b3.pth     ← from zip
├── resnet50.pth            ← from zip
└── inference_config.json   ← already in repo ✅
```

3. Do **not** replace `inference_config.json` — it's already there.

---

## What this model does

Classifies thermal cat images as **Healthy** or **Sick** using an ensemble of 3 models:
- `custom_cnn.pth` — Custom CNN (weight: 20%)
- `efficientnet_b3.pth` — EfficientNet-B3 (weight: 50%)
- `resnet50.pth` — ResNet50 (weight: 30%)

Accepts **PNG, JPG, WEBP** thermal images (RGB).
