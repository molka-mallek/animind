# AniMind — AI-Powered Animal Health & Behavior Platform

> Deep learning platform for animal behavior recognition, disease detection, and health monitoring across pets, poultry, livestock, and wildlife.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57+-ff4b4b.svg)](https://streamlit.io/)

---

## Overview

**AniMind** is a full-stack AI platform that analyses animal behavior and health through computer vision, audio processing, and deep learning. It provides real-time insights for pet owners, veterinarians, and farmers.

**Institution:** École Supérieure Privée d'Ingénierie et de Technologie — Esprit  
**Contact:** Cortexa@gmail.com | +216 12 345 678  
**Blog:** https://ilefbennour10.wixsite.com/my-site-1/about-4

---

## Available Features

| Module | Input | Model |
|---|---|---|
| 🐶 Dog Emotion Analysis | Photo / Video | CNN + YOLOv8 |
| 👁️ Eye Infection Detection | Photo | ResNet18 |
| 🔬 Skin Anomaly Detection | Photo | EfficientNet + U-Net |
| 🧠 Behavioral Disease Detection | Video | ST-GCN + YOLO-Pose |
| 🐔 Chicken Fowlpox Detection | Photo | EfficientNet-B0 |
| 🧪 Bird Droppings Analysis | Photo | ResNet18 |
| 🐄 Real-Time Calf Monitoring | Sensor (accelerometer) | GRU |
| 🐟 Fish Freshness Analysis | Photo | YOLO + SAM2 + DualStream EfficientNet-B0 |
| 🎵 Bird Species Classification | Audio (.wav / .mp3) | Custom BirdCNN (mel-spectrogram) |
| 🧬 Rabies Detection | Photo | CNN |

---

## Architecture

```
animind/
├── frontend/                    # React 19 + Vite web app
│   ├── src/
│   │   ├── components/          # Layout, Navbar, Sidebar
│   │   ├── pages/               # Home, Dashboard, Modules
│   │   ├── modules/             # One JSX file per AI feature
│   │   └── data/modules.js      # Central module registry
│   └── public/                  # Static assets (bird images, logo)
│
└── backend/                     # FastAPI + Python
    ├── main.py                  # API routes (lazy-loaded pipelines)
    ├── calf_dashboard.py        # Streamlit real-time dashboard
    ├── modules/                 # AI inference pipelines
    │   ├── dog_emotion/
    │   ├── calf_behavior/
    │   ├── cat and dogs eye infection/
    │   ├── chiken/
    │   ├── skin_anomaly/
    │   ├── ataxia/
    │   ├── fish_freshness/      # YOLO + SAM2 + DualStream EfficientNet
    │   └── xeno/                # BirdCNN mel-spectrogram classifier
    └── model/                   # Model weights (download separately)
        ├── calf_behavior/       # GRU weights + scaler + encoder
        ├── fish_freshness/      # fish_model.pth + yolo26n.pt + sam2.1_hiera_large.pt
        └── xeno/                # bird_model.pth
```

---

## ⚠️ Model Files — Download Required

Model weights are **not included in this repository** (too large for git).

### Download all models from Google Drive:

**🔗 [Download Models — Google Drive](https://drive.google.com/drive/folders/19xoYa18GhGoznFl4gE2HlXB5jVkROgfn?usp=sharing)**

The Drive folder contains:
- `fish_model.pth` — DualStream EfficientNet-B0 fish freshness classifier
- `bird_model.pth` — BirdCNN mel-spectrogram species classifier
- `yolo26n.pt` — Custom YOLO for fish eye/gill ROI detection
- `sam2.1_hiera_large.pt` — SAM 2.1 segmentation model *(large file, ~2.4 GB)*
- Other model files referenced in the README

### Where to place them:

```
backend/model/
├── fish_freshness/
│   ├── fish_model.pth              ← from Drive
│   ├── yolo26n.pt                  ← from Drive
│   └── sam2.1_hiera_large.pt       ← from Drive (optional, ~2.4 GB)
├── xeno/
│   └── bird_model.pth              ← from Drive
├── calf_behavior/
│   ├── model.keras                 ← from Drive
│   ├── scaler.pkl                  ← from Drive
│   └── label_encoder.pkl           ← from Drive
└── (other models from Drive)
```

> **Note:** `sam2.1_hiera_large.pt` is optional. Without it, the fish freshness pipeline falls back to plain YOLO bounding-box crops instead of SAM-segmented crops. The endpoint still works — accuracy may be slightly lower.

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/animind.git
cd animind
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install SAM2 (required for fish freshness full pipeline)
pip install "git+https://github.com/facebookresearch/sam2.git"
```

### 3. Download model files

Download from the [Google Drive link](https://drive.google.com/drive/folders/19xoYa18GhGoznFl4gE2HlXB5jVkROgfn?usp=sharing) and place them in `backend/model/` as shown above.

### 4. Frontend setup

```bash
cd frontend
npm install
```

---

## Running the Application

You need **3 terminals** for the full experience:

**Terminal 1 — Backend API (port 8000):**
```bash
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend (port 5173):**
```bash
cd frontend
npm run dev
```

**Terminal 3 — Calf Monitoring Dashboard (port 8501):**
```bash
cd backend
venv\Scripts\streamlit.exe run calf_dashboard.py --server.port 8501
```

Then open **http://localhost:5173** in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/predict` | Dog emotion (image) |
| POST | `/predict-video` | Dog emotion (video) |
| POST | `/predict-calf` | Calf behavior (sensor JSON) |
| POST | `/predict-eye-infection` | Eye infection (image) |
| POST | `/predict-chicken-fowlpox` | Fowlpox (image) |
| POST | `/predict-bird-droppings` | Bird droppings (image) |
| POST | `/predict-skin-anomaly` | Skin anomaly (image) |
| POST | `/predict-ataxia` | Behavioral disease (video) |
| POST | `/predict-fish-freshness` | Fish freshness (image) |
| POST | `/predict-bird-species` | Bird species (audio) |

Interactive docs: **http://localhost:8000/docs**

---

## Fish Freshness Pipeline

The fish freshness module runs a 3-step pipeline:

1. **YOLO** (`yolo26n.pt`) — detects eye and gill bounding boxes on the fish image
2. **SAM 2.1** (`sam2.1_hiera_large.pt`) — segments and crops each ROI cleanly
3. **DualStream EfficientNet-B0** (`fish_model.pth`) — takes both crops, outputs C1/C2/C3 grade + score 0–100

The `roi_status` field in the response tells you which path was used:
- `yolo+sam` — full pipeline
- `yolo_bbox` — YOLO found ROIs but SAM not installed
- `centre_crop_fallback` — no fish ROIs detected

## Bird Species Pipeline

The bird species module:

1. Loads the audio file with `librosa` (resampled to 22050 Hz)
2. Computes a mel-spectrogram (128 mels, normalised with global mean/std from training)
3. Feeds the single-channel spectrogram into a custom **BirdCNN** (4 conv blocks + AdaptiveAvgPool + FC)
4. Returns the predicted species with confidence and probabilities for all 5 classes

**Supported species:** Common Cuckoo · Eurasian Blackcap · Great Tit · Grey-breasted Wood Wren · House Wren

---

## Troubleshooting

**Backend not starting:**
```bash
pip install -r requirements.txt
```

**`No module named 'sam2'`:**
```bash
pip install "git+https://github.com/facebookresearch/sam2.git"
```

**`No module named 'timm'`:**
```bash
pip install timm
```

**`No module named 'librosa'`:**
```bash
pip install librosa soundfile
```

**Fish/bird model not found:**
→ Download from the [Google Drive link](https://drive.google.com/drive/folders/19xoYa18GhGoznFl4gE2HlXB5jVkROgfn?usp=sharing) and place in `backend/model/`

**CORS error in browser:**
→ Make sure the backend is running on port 8000 before opening the frontend

**Calf dashboard shows "System offline":**
→ Start the FastAPI backend first, then run Streamlit

---

## Tech Stack

- **Frontend:** React 19, Vite, React Router, CSS Modules
- **Backend:** FastAPI, Uvicorn, Pydantic
- **AI/ML:** PyTorch, TensorFlow/Keras, timm, Ultralytics YOLOv8, SAM2, librosa, OpenCV, scikit-learn
- **Dashboard:** Streamlit, Matplotlib
- **Models:** EfficientNet-B0, ResNet18, U-Net, GRU, BirdCNN, DualStream EfficientNet, ST-GCN

---

## License

MIT License — see [LICENSE](LICENSE) for details.
