# Cat Vocalization Classification — Model Files

The head model file is **not included in the repository** (too large for git).
Download it below and place it in this folder.

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

3. Do **not** replace `metadata.json` — it's already there.
4. The `yamnet_cache/` folder is created automatically the **first time** the model runs (requires internet on first run only, ~25 MB download).

---

## What this model does

Classifies cat vocalizations into **10 behavioral categories**:
`Angry`, `Defence`, `Fighting`, `Happy`, `HuntingMind`, `Mating`, `MotherCall`, `Paining`, `Resting`, `Warning`

Triggers a **pain alert** when `Paining` probability exceeds 35%.
Accepts **MP3 / WAV** audio files (1–3 seconds ideal).
