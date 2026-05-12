# AniMind — AI-Powered Animal Behavior Analysis Platform

> Deep learning-based animal behavior recognition and health monitoring system for pets and livestock

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14+-orange.svg)](https://www.tensorflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Overview

**AniMind** is an artificial intelligence platform that analyzes animal behavior and health through computer vision, deep learning and more. The system provides real time insights for pet owners, veterinarians, and farmers to better understand and monitor animal welfare.

The platform combines multiple AI models for emotion detection, behavior classification, disease detection, and anomaly recognition across various animal species including dogs, cats, horses, birds, and livestock.

**Institution:** École Supérieure Privée d'Ingénierie et de Technologie — Esprit  
**Contact:** Cortexa@gmail.com | +216 12 345 678  
**Blog:** https://ilefbennour10.wixsite.com/my-site-1/about-4

**Key Capabilities:**
- Real-time emotion and behavior analysis from images and videos
- Live IoT sensor monitoring for livestock behavior tracking
- Multi-species support (dogs, cats, horses, birds, cattle, poultry, fish)
- Health anomaly detection and early warning systems
- Audio-based bird species classification from song recordings
- Fish freshness grading with ROI detection and segmentation
- Scalable REST API architecture for integration

**Use Cases:**
- Pet owners monitoring emotional well-being
- Veterinary diagnostics and health screening
- Farm management and livestock monitoring
- Animal welfare research and behavioral studies

---

## Features

### Current Features (Available)
- ✅ **Dog Emotion Recognition** — Classify dog emotions from photos/videos (happy, sad, angry, relaxed, fearful)
- ✅ **Real-Time Calf Behavior Monitoring** — Live accelerometer-based behavior classification (lying, standing, eating, active, social, abnormal)
- ✅ **Eye Infection Detection** — Screen for eye infections in cats and dogs using ResNet18-based classification
- ✅ **Chicken Fowlpox Detection** — Identify fowlpox disease in poultry using EfficientNet-B0 architecture
- ✅ **Bird Droppings Analysis** — Assess bird health through fecal matter analysis using ResNet18
- ✅ **Skin Anomaly Detection** — Detect and segment skin diseases in cats and dogs using U-Net with medical-grade visualization
- ✅ **Behavioral Disease Detection** — Detect neurological and behavioral disorders in dogs and cats via video (ST-GCN + YOLO-Pose)
- ✅ **Rabies Detection** — Screen for rabies-related symptoms from animal photos using EfficientNet-B0
- ✅ **Fish Freshness Analysis** — Grade fish freshness (C1/C2/C3, score 0–100) using YOLO ROI detection + SAM2 segmentation + DualStream EfficientNet-B0
- ✅ **Bird Species Classification** — Identify bird species from audio recordings using mel-spectrogram analysis and a custom BirdCNN (5 species)
- ✅ **Cat Vocalization Analysis** — Classify cat sounds into 10 behavioral categories with pain detection
- ✅ **Horse Pain Detection** — Identify pain indicators through BiLSTM behavioral analysis from video
- ✅ **Thermal Cat Health Screening** — Screen for health issues using thermal imaging with ensemble AI (ResNet50, EfficientNet-B3, Custom CNN)
- ✅ **Multi-Modal Analysis** — Support for image, video, audio, thermal, and sensor data inputs
- ✅ **Interactive Dashboard** — Streamlit-based real-time calf monitoring interface with intelligent alerts
- ✅ **REST API** — FastAPI backend for scalable deployment
- ✅ **Responsive Web Interface** — React-based frontend for easy access

### Upcoming Features (In Development)
- 🔜 **Multi-language Support** — Interface localization
- 🔜 **Historical Data Analytics** — Long-term behavior trend analysis
- 🔜 **Mobile Application** — iOS and Android apps for on-the-go monitoring

---

## Tech Stack

### Frontend
- **React 19** — Modern UI framework with hooks and context
- **Vite** — Fast build tool and development server
- **React Router** — Client-side routing and navigation
- **CSS Modules** — Scoped styling and component isolation

### Backend
- **FastAPI** — High-performance Python web framework
- **Uvicorn** — ASGI server for async request handling
- **Pydantic** — Data validation and serialization
- **Python 3.9+** — Core programming language

### AI / Machine Learning
- **TensorFlow / Keras** — Deep learning model training and inference
- **PyTorch / torchvision** — Model inference for PyTorch-based models
- **timm** — EfficientNet-B0 backbone for fish freshness classifier
- **OpenCV** — Computer vision and image processing
- **Ultralytics YOLOv8** — Object detection and face localization
- **SAM2 (Segment Anything Model 2.1)** — ROI segmentation for fish freshness pipeline
- **librosa** — Audio processing and mel-spectrogram computation
- **scikit-learn** — Feature engineering and preprocessing
- **NumPy** — Numerical computing and array operations
- **Pandas** — Data manipulation and analysis

### Dashboard & Visualization
- **Streamlit** — Interactive real-time monitoring dashboard
- **Matplotlib** — Data visualization and plotting
- **Plotly** — Interactive charts and graphs

### Model Architectures
- **CNN (Convolutional Neural Networks)** — Image-based emotion recognition
- **BirdCNN** — Custom 4-block CNN for mel-spectrogram bird species classification
- **ResNet18** — Eye infection and bird droppings classification
- **EfficientNet-B0** — Chicken fowlpox detection; DualStream backbone for fish freshness
- **DualStream EfficientNet-B0** — Two-stream architecture (eye crop + gill crop) for fish freshness grading
- **U-Net with Attention Gates** — Skin anomaly segmentation
- **VGG16 / ResNet50** — Animal classification and anomaly detection
- **GRU (Gated Recurrent Units)** — Time-series behavior classification for calves
- **ST-GCN** — Spatial-temporal graph CNN for behavioral disease detection
- **Transfer Learning** — Pre-trained models for feature extraction
- **Ensemble Methods** — Multi-model prediction aggregation

### Data Processing
- **Feature Engineering** — ODBA, VeDBA, pitch, roll calculations
- **Mel-Spectrogram** — Audio-to-image conversion for bird species classification
- **StandardScaler** — Data normalization and standardization
- **LabelEncoder** — Categorical variable encoding
- **Data Augmentation** — Image transformations for model robustness

### Deployment & DevOps
- **Docker** (planned) — Containerization for consistent deployment
- **REST API** — Stateless architecture for scalability
- **CORS Middleware** — Cross-origin resource sharing
- **Multi-process Architecture** — Separate frontend, backend, and dashboard services

---

## Directory Structure

```
animind/
│
├── frontend/                          # React web application
│   ├── src/
│   │   ├── components/                # Reusable UI components
│   │   │   ├── Layout.jsx             # Main layout wrapper
│   │   │   ├── Navbar.jsx             # Navigation bar
│   │   │   └── Sidebar.jsx            # Side navigation
│   │   ├── pages/                     # Route pages
│   │   │   ├── Home.jsx               # Landing page (with footer)
│   │   │   ├── Modules.jsx            # Feature selection with category filter
│   │   │   └── Dashboard.jsx          # Analytics dashboard with category filter
│   │   ├── modules/                   # Feature modules
│   │   │   ├── DogEmotion.jsx         # Dog emotion analysis UI
│   │   │   ├── EyeInfection.jsx       # Eye infection detection UI
│   │   │   ├── ChickenFowlpox.jsx     # Fowlpox detection UI
│   │   │   ├── BirdDroppings.jsx      # Bird droppings analysis UI
│   │   │   ├── SkinAnomaly.jsx        # Skin anomaly detection UI
│   │   │   ├── BehavioralDisease.jsx  # Behavioral disease detection UI
│   │   │   ├── RabiesDetection.jsx    # Rabies detection UI
│   │   │   ├── FishFreshness.jsx      # Fish freshness analysis UI
│   │   │   └── BirdSpecies.jsx        # Bird species classification UI
│   │   ├── data/
│   │   │   └── modules.js             # Module configuration with categories
│   │   ├── App.jsx                    # Root component with all routes
│   │   └── main.jsx                   # Entry point
│   ├── public/                        # Static assets
│   │   ├── cortexa.png                # Cortexa logo
│   │   ├── common cuckoo.jpg          # Bird species images
│   │   ├── Eurasian Blackcap.jpg
│   │   ├── Great Tit.jpg
│   │   ├── Grey-breasted Wood Wren.jpg
│   │   └── House Wren.jpg
│   ├── package.json                   # Node dependencies
│   └── vite.config.js                 # Build configuration
│
├── backend/                           # Python FastAPI server
│   ├── modules/                       # AI pipeline modules
│   │   ├── dog_emotion/
│   │   │   └── ai_pipeline.py         # Dog emotion inference
│   │   ├── calf_behavior/
│   │   │   └── ai_pipeline.py         # Calf behavior inference
│   │   ├── cat and dogs eye infection/
│   │   │   ├── ai_pipeline.py         # Eye infection detection
│   │   │   └── cat_eye_infection_resnet18_best.pth
│   │   ├── chiken/
│   │   │   ├── fowlpox_ai_pipeline.py
│   │   │   ├── fowlpox_efficientnet_b0_best.pth
│   │   │   ├── bird_droppings_ai_pipeline.py
│   │   │   └── bird_droppings_resnet18_best.pth
│   │   ├── skin_anomaly/
│   │   │   └── ai_pipeline.py         # Skin anomaly detection & segmentation
│   │   ├── ataxia/
│   │   │   └── ai_pipeline.py         # Behavioral disease detection
│   │   ├── fish_freshness/
│   │   │   └── ai_pipeline.py         # YOLO + SAM2 + DualStream EfficientNet
│   │   └── xeno/
│   │       └── ai_pipeline.py         # BirdCNN mel-spectrogram classifier
│   ├── model/                         # Trained models (download separately)
│   │   ├── dog_emotion_best_model.keras
│   │   ├── best_classifier.h5         # Animal classifier (cat/dog)
│   │   ├── best_anomaly_detector.h5   # Anomaly detector
│   │   ├── unet_segmentation.h5       # U-Net segmentation model
│   │   ├── skin_anomaly_metadata.json # Model configuration
│   │   ├── calf_behavior/
│   │   │   ├── model.keras            # GRU model
│   │   │   ├── scaler.pkl             # Feature scaler
│   │   │   ├── label_encoder.pkl      # Class encoder
│   │   │   └── model_metadata.json    # Model config
│   │   ├── fish_freshness/
│   │   │   ├── fish_model.pth         # DualStream EfficientNet-B0
│   │   │   ├── yolo26n.pt             # Custom YOLO for ROI detection
│   │   │   └── sam2.1_hiera_large.pt  # SAM 2.1 segmentation (~2.4 GB)
│   │   └── xeno/
│   │       └── bird_model.pth         # BirdCNN weights
│   ├── main.py                        # FastAPI application
│   ├── calf_dashboard.py              # Streamlit dashboard
│   └── requirements.txt               # Python dependencies
│
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

---

## ⚠️ Before You Start — Download the Models

The AI model files are not included in this repo (too large for git).

### **Required Model Files:**

1. **Fish Freshness + Bird Species Models (NEW):**
   - Download from: **[Google Drive — Fish & Bird Models](https://drive.google.com/drive/folders/19xoYa18GhGoznFl4gE2HlXB5jVkROgfn?usp=sharing)**
   - Place in `backend/model/`:
     ```
     backend/model/
     ├── fish_freshness/
     │   ├── fish_model.pth              ← DualStream EfficientNet-B0
     │   ├── yolo26n.pt                  ← Custom YOLO ROI detector
     │   └── sam2.1_hiera_large.pt       ← SAM 2.1 (~2.4 GB, optional)
     └── xeno/
         └── bird_model.pth              ← BirdCNN
     ```
   > **Note on SAM2:** `sam2.1_hiera_large.pt` is optional (~2.4 GB). Without it, the fish pipeline falls back to plain YOLO bounding-box crops. The endpoint still works — accuracy may be slightly lower.

2. **Dog Emotion Model:**
   - Download `dog_emotion_best_model.keras` from: [Google Drive Link](https://drive.google.com/file/d/15Zh-ydHIT5wkYkUiWmHzCXhz1pB4JXmy/view?usp=sharing)
   - Place it here: `backend/model/dog_emotion_best_model.keras`

3. **Skin Anomaly Detection Models:**
   - Download from: [Google Drive Link](https://drive.google.com/drive/folders/1Qa04B8OLaRj0VUHr9s5p7CVlVjYL_lEF?usp=sharing)
   - Extract and place in `backend/model/`:
     ```
     backend/model/
     ├── best_classifier.h5          # Animal classifier (cat/dog)
     ├── best_anomaly_detector.h5    # Anomaly detector
     ├── unet_segmentation.h5        # U-Net segmentation
     └── skin_anomaly_metadata.json  # Already included in repo
     ```

4. **Behavioral Disease Detection Models:**
   - Download from your teammate or contact project maintainers
   - Place in `backend/`:
     ```
     backend/
     ├── yolo11n-pose.pt              ← YOLO pose detection model
     └── model/
         └── stgcn_multiclass.pth     ← ST-GCN model for gait analysis
     ```

5. **Rabies Detection Model:**
   - Model file: `rabies_efficientnet_b0_best.pth`
   - Already included in: `backend/modules/rabies_detection/`

6. **Other Models:**
   - Eye infection, fowlpox, bird droppings, cat sound, horse pain, and thermal cat models are already included in their respective module folders

### **Quick Setup:**
```bash
# Option 1: Manual download (recommended)
# Download from the links above and place in backend/model/

# Option 2: Use download script
cd backend
pip install gdown
python download_models.py
```

---

## 🚀 Running the Application

Make sure you have **Python 3.9+** and **Node.js 18+** installed.

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Required for fish freshness full pipeline (SAM2)
pip install "git+https://github.com/facebookresearch/sam2.git"

# Required for bird species classification
pip install librosa soundfile timm
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Run All Services (3 Terminals)

**Terminal 1 — Backend API:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Access at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

**Terminal 2 — Frontend Web App:**
```bash
cd frontend
npm run dev
```
Access at: `http://localhost:5173`

**Terminal 3 — Calf Monitoring Dashboard:**
```bash
cd backend
streamlit run calf_dashboard.py
```
Access at: `http://localhost:8501`

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

---

## Usage

### Dog Emotion Analysis
1. Navigate to `http://localhost:5173`
2. Click "Start Analysis"
3. Select "Dog Emotion Analysis"
4. Upload a photo or video of your dog
5. View emotion classification results (happy, sad, angry, relaxed, fearful)

### Calf Behavior Monitoring
1. Navigate to `http://localhost:8501`
2. Select a calf from the dropdown (calf_1 through calf_6)
3. Toggle "Demo mode" to simulate sensor data
4. Monitor real-time behavior classification
5. Respond to alerts (abnormal behavior, lying streak, etc.)

### Eye Infection Detection
1. Navigate to `http://localhost:5173`
2. Click "Start Analysis" → "Eye Infection Detection"
3. Upload a clear eye photo of your cat or dog
4. View infection screening results

### Chicken Fowlpox / Bird Droppings Analysis
1. Navigate to `http://localhost:5173`
2. Select the appropriate module
3. Upload a clear photo
4. View health assessment results

### Skin Anomaly Detection
1. Navigate to `http://localhost:5173`
2. Select "Skin Anomaly Detection"
3. Upload a close-up photo of your cat or dog's skin
4. View the 3-step analysis:
   - **Step 1:** Animal identification (cat/dog)
   - **Step 2:** Anomaly detection (healthy/anomaly)
   - **Step 3:** Affected area segmentation with medical-grade visualization
5. Review visual indicators and veterinary recommendations

### Fish Freshness Analysis (NEW)
1. Navigate to `http://localhost:5173`
2. Select "Fish Freshness Analysis"
3. Upload a photo of the fish
4. The pipeline automatically:
   - Detects eye and gill regions (YOLO)
   - Segments each ROI (SAM 2.1)
   - Classifies freshness (DualStream EfficientNet-B0)
5. View grade (C1/C2/C3), score (0–100), and recommendations

### Bird Species Classification (NEW)
1. Navigate to `http://localhost:5173`
2. Select "Bird Species Classification"
3. Upload an audio recording (.wav, .mp3, .ogg, .flac, .m4a)
4. The pipeline converts audio → mel-spectrogram → BirdCNN inference
5. View the identified species, confidence, description, habitat, and fun fact

**Supported species:** Common Cuckoo · Eurasian Blackcap · Great Tit · Grey-breasted Wood Wren · House Wren

### API Usage
```python
import requests

# Dog emotion analysis
with open('dog_photo.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )
    result = response.json()
    print(f"Emotion: {result['emotion']}")
    print(f"Confidence: {result['confidence']}")

# Calf behavior prediction
response = requests.post(
    'http://localhost:8000/predict-calf',
    json={'id': 'calf_1', 'accX': 0.95, 'accY': -0.10, 'accZ': 0.05}
)
result = response.json()
print(f"Behavior: {result['result']['behavior']}")

# Skin anomaly detection
with open('cat_skin.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict-skin-anomaly',
        files={'file': f}
    )
    result = response.json()
    print(f"Animal: {result['animal_label']}")
    print(f"Status: {result['status_label']}")
    if result['segmentation_done']:
        print(f"Affected area: {result['seg_area_pct']}%")

# Fish freshness
with open('fish.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict-fish-freshness',
        files={'file': f}
    )
    result = response.json()
    print(f"Grade: {result['grade']}  Score: {result['score']}/100")
    print(f"ROI method: {result['roi_status']}")

# Bird species from audio
with open('bird_song.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict-bird-species',
        files={'file': f}
    )
    result = response.json()
    print(f"Species: {result['display_name']}  Confidence: {result['confidence']:.0%}")
```

---

## 🧩 Available Features

| Feature | Status |
|---|---|
| Dog Emotion Analysis (photo + video) | ✅ Ready |
| Calf Behavior Monitoring (real-time) | ✅ Ready |
| Eye Infection Detection (cats/dogs) | ✅ Ready |
| Chicken Fowlpox Detection | ✅ Ready |
| Skin Anomaly Detection & Segmentation | ✅ Ready |
| Bird Droppings Analysis | ✅ Ready |
| Behavioral Disease Detection | ✅ Ready |
| Rabies Detection | ✅ Ready |
| Fish Freshness Analysis | ✅ Ready |
| Bird Species Classification (audio) | ✅ Ready |
| Cat Behavior Classification | 🔜 Coming soon |
| Dog Vocalization Analysis | 🔜 Coming soon |
| Horse Pain Detection | 🔜 Coming soon |
| Wound Detection | 🔜 Coming soon |
| Breed Identification | 🔜 Coming soon |
| Activity & Vitals Tracker | 🔜 Coming soon |

---

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, React Router, CSS Modules
- **Backend:** FastAPI, Uvicorn, Pydantic
- **AI/ML:** TensorFlow/Keras, PyTorch, timm, Ultralytics YOLOv8, SAM2, librosa, OpenCV, scikit-learn
- **Dashboard:** Streamlit, Matplotlib

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

**Model not found error:**
```
FileNotFoundError: model.keras / .pth not found
```
→ Download model files from the Drive links above and place in `backend/model/`

**CORS error:**
```
Access to fetch blocked by CORS policy
```
→ Ensure backend is running on port 8000 before starting frontend

**Dashboard not connecting:**
```
Backend offline — please contact support
```
→ Start backend first: `uvicorn main:app --port 8000`

**Frontend not loading:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## Roadmap

### Phase 1 (Current — 2026)
- ✅ Dog emotion recognition
- ✅ Calf behavior monitoring
- ✅ Eye infection detection (cats/dogs)
- ✅ Chicken fowlpox detection
- ✅ Bird droppings analysis
- ✅ Skin anomaly detection & segmentation
- ✅ Behavioral disease detection
- ✅ Rabies detection
- ✅ Fish freshness analysis
- ✅ Bird species classification (audio)
- ✅ REST API
- ✅ Responsive web interface
- ✅ Real-time calf dashboard

### Phase 2 (Q2 2026)
- 🔜 Cat behavior classification
- 🔜 Horse pain detection
- 🔜 Dog vocalization analysis
- 🔜 Multi-language support

### Phase 3 (Q3 2026)
- 🔜 Wound detection and severity assessment
- 🔜 Breed identification system
- 🔜 Activity and vitals tracking
- 🔜 Advanced analytics dashboard

### Phase 4 (Q4 2026)
- 🔜 Mobile application (iOS/Android)
- 🔜 Cloud deployment
- 🔜 User authentication
- 🔜 Historical data analytics
- 🔜 Multi-farm management

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Areas for contribution:**
- New animal species support
- Additional behavior classes
- Model optimization
- UI/UX improvements
- Documentation
- Testing

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

This project was developed as part of the **Artificial Intelligence and Machine Learning** curriculum at **École Supérieure Privée d'Ingénierie et de Technologie — Esprit**.

**Special Thanks:**
- **AcTBeCalf Dataset** — Calf behavior training data
- **TensorFlow Team** — Deep learning framework
- **FastAPI Community** — Web framework
- **Streamlit Team** — Dashboard framework
- **Open Source Community** — Libraries and tools

**Academic Supervision:**
- École Supérieure Privée d'Ingénierie et de Technologie — Esprit
- AI & ML Department

---

## Contact

**Project Team:** Cortexa — AniMind Development Team  
**Institution:** École Supérieure Privée d'Ingénierie et de Technologie — Esprit  
**Email:** Cortexa@gmail.com  
**Phone:** +216 12 345 678  
**Blog:** https://ilefbennour10.wixsite.com/my-site-1/about-4  
**GitHub:** https://github.com/your-username/animind

---

## Citation

If you use this project in your research, please cite:

```bibtex
@software{animind2026,
  title={AniMind: AI-Powered Animal Behavior Analysis Platform},
  author={Cortexa Team},
  year={2026},
  institution={Esprit School of Engineering},
  url={https://github.com/your-username/animind}
}
```
