# Horse Pain Detection — Model Files

These files are **not included in the repository** (binary model files).
Download the zip below, extract it, and place the files in this folder.

---

## Download

📦 **[Download horse_pain_models.zip](https://drive.google.com/drive/folders/1oRmKHZnCMFUJ1lXBcLG6BpRCrUvaronf?usp=sharing)** (~0.6 MB)

---

## After downloading

1. Extract the zip
2. Place all 3 files in `backend/model/horse_pain/` so it looks like this:

```
backend/model/horse_pain/
├── behavior_bilstm.pt    ← from zip
├── train_mean.npy        ← from zip
└── train_std.npy         ← from zip
```

---

## What this model does

Detects **pain indicators** in horses from video footage using a BiLSTM model.
Outputs: `Pain Detected` or `No Pain` with a confidence score.
Accepts **MP4, MOV, AVI** video files.
