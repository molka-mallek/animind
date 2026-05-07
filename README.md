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

**Key Capabilities:**
- Real-time emotion and behavior analysis from images and videos
- Live IoT sensor monitoring for livestock behavior tracking
- Multi-species support (dogs, cats, horses, birds, cattle, poultry)
- Health anomaly detection and early warning systems
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
- ✅ **Multi-Modal Analysis** — Support for image, video, and sensor data inputs
- ✅ **Interactive Dashboard** — Streamlit-based real-time monitoring interface
- ✅ **REST API** — FastAPI backend for scalable deployment
- ✅ **Responsive Web Interface** — React-based frontend for easy access

### Upcoming Features (In Development)
- 🔜 **Cat Behavior Classification** — Emotion and activity recognition for cats
- 🔜 **Behavioral Disease Detection** — Identify neurological and behavioral disorders
- 🔜 **Dog Vocalization Analysis** — Audio-based emotion detection from barks and whines
- 🔜 **Horse Pain Detection** — Video analysis for pain and discomfort indicators
- 🔜 **Skin Anomaly Detection** — Dermatological disease detection in dogs and cats
- 🔜 **Multi-language Support** — Interface localization

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
- **OpenCV** — Computer vision and image processing
- **Ultralytics YOLOv8** — Object detection and face localization
- **scikit-learn** — Feature engineering and preprocessing
- **NumPy** — Numerical computing and array operations
- **Pandas** — Data manipulation and analysis

### Dashboard & Visualization
- **Streamlit** — Interactive real-time monitoring dashboard
- **Matplotlib** — Data visualization and plotting
- **Plotly** — Interactive charts and graphs

### Model Architectures
- **CNN (Convolutional Neural Networks)** — Image-based emotion recognition
- **ResNet18** — Eye infection and bird droppings classification
- **EfficientNet-B0** — Chicken fowlpox detection
- **GRU (Gated Recurrent Units)** — Time-series behavior classification
- **Transfer Learning** — Pre-trained models for feature extraction
- **Ensemble Methods** — Multi-model prediction aggregation

### Data Processing
- **Feature Engineering** — ODBA, VeDBA, pitch, roll calculations
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
│   │   │   ├── Home.jsx               # Landing page
│   │   │   ├── Modules.jsx            # Feature selection
│   │   │   └── Dashboard.jsx          # Analytics dashboard
│   │   ├── modules/                   # Feature modules
│   │   │   ├── DogEmotion.jsx         # Dog emotion analysis UI
│   │   │   ├── EyeInfection.jsx       # Eye infection detection UI
│   │   │   ├── ChickenFowlpox.jsx     # Fowlpox detection UI
│   │   │   └── BirdDroppings.jsx      # Bird droppings analysis UI
│   │   ├── data/
│   │   │   └── modules.js             # Module configuration
│   │   ├── App.jsx                    # Root component
│   │   └── main.jsx                   # Entry point
│   ├── public/                        # Static assets
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
│   │   └── chiken/
│   │       ├── fowlpox_ai_pipeline.py # Fowlpox detection
│   │       ├── fowlpox_efficientnet_b0_best.pth
│   │       ├── bird_droppings_ai_pipeline.py
│   │       └── bird_droppings_resnet18_best.pth
│   ├── model/                         # Trained models
│   │   ├── dog_emotion_best_model.keras
│   │   └── calf_behavior/
│   │       ├── model.keras            # GRU model
│   │       ├── scaler.pkl             # Feature scaler
│   │       ├── label_encoder.pkl      # Class encoder
│   │       └── model_metadata.json    # Model config
│   ├── main.py                        # FastAPI application
│   ├── calf_dashboard.py              # Streamlit dashboard
│   ├── requirements.txt               # Python dependencies
│
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

---

## Getting Started

### Prerequisites

- **Python 3.9+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **pip** — Python package manager
- **npm** — Node package manager

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/animind.git
cd animind
```

#### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

**Required Python packages:**
- `fastapi>=0.104.0` — Web framework
- `uvicorn>=0.24.0` — ASGI server
- `tensorflow>=2.14.0` — Deep learning
- `opencv-python>=4.8.0` — Computer vision
- `streamlit>=1.32.0` — Dashboard
- `scikit-learn>=1.3.0` — ML utilities
- `numpy>=1.24.0` — Numerical computing
- `pandas>=2.0.0` — Data manipulation

#### 3. Frontend Setup
```bash
cd frontend
npm install
```

**Required Node packages:**
- `react@19` — UI framework
- `react-router-dom` — Routing
- `vite` — Build tool

#### 4. Model Files Setup

⚠️ **Important:** Model files are not included in the repository due to size constraints.

Download the trained models from: [[Google Drive Link / HuggingFace Link](https://drive.google.com/file/d/15Zh-ydHIT5wkYkUiWmHzCXhz1pB4JXmy/view?usp=sharing)]

Place them in the following structure:
```
backend/model/
├── dog_emotion_best_model.keras
└── calf_behavior/
    ├── model.keras
    ├── scaler.pkl
    ├── label_encoder.pkl
    └── model_metadata.json
```

### Running the Application

#### Option 1: Run All Services (3 Terminals)

**Terminal 1 — Backend API:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Access at: `http://localhost:8000`

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

#### Option 2: Run Individual Services

**Backend Only:**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend Only:**
```bash
cd frontend
npm run dev
```

**Dashboard Only:**
```bash
cd backend
streamlit run calf_dashboard.py
```

### Usage

#### Dog Emotion Analysis
1. Navigate to `http://localhost:5173`
2. Click "Start Analysis"
3. Select "Dog Emotion Analysis"
4. Upload a photo or video of your dog
5. View emotion classification results (happy, sad, angry, relaxed, fearful)

#### Calf Behavior Monitoring
1. Navigate to `http://localhost:8501`
2. Select a calf from the dropdown (calf_1 through calf_6)
3. Toggle "Demo mode" to simulate sensor data
4. Monitor real-time behavior classification
5. Respond to alerts (abnormal behavior, lying streak, etc.)

#### Eye Infection Detection
1. Navigate to `http://localhost:5173`
2. Click "Start Analysis"
3. Select "Eye Infection Detection"
4. Upload a clear eye photo of your cat or dog
5. View infection screening results

#### Chicken Fowlpox / Bird Droppings Analysis
1. Navigate to `http://localhost:5173`
2. Click "Start Analysis"
3. Select the appropriate module
4. Upload a clear photo
5. View health assessment results

#### API Usage
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
    json={
        'id': 'calf_1',
        'accX': 0.95,
        'accY': -0.10,
        'accZ': 0.05
    }
)
result = response.json()
print(f"Behavior: {result['result']['behavior']}")
```

---

## Model & Methodology

### Dog Emotion Recognition
- **Architecture:** CNN with transfer learning (pre-trained on ImageNet)
- **Input:** RGB images (224×224 pixels)
- **Output:** 5 emotion classes (happy, sad, angry, relaxed, fearful)
- **Preprocessing:** Face detection with YOLOv8, cropping, normalization
- **Training:** Custom dataset with data augmentation
- **Accuracy:** ~85% on validation set

### Calf Behavior Classification
- **Architecture:** GRU (Gated Recurrent Unit) with 2 layers
- **Input:** 100 samples × 8 features (4 seconds at 25 Hz)
- **Features:** accX, accY, accZ, magnitude, ODBA, VeDBA, pitch, roll
- **Output:** 6 behavior classes (lying, standing, eating_drinking, active, social, abnormal)
- **Dataset:** AcTBeCalf (30 calves, accelerometer data)
- **Accuracy:** ~85-90% on validation set

### Feature Engineering
- **ODBA (Overall Dynamic Body Acceleration)** — Activity intensity metric
- **VeDBA (Vectorial Dynamic Body Acceleration)** — Movement magnitude
- **Pitch & Roll** — Body orientation angles
- **Magnitude** — Total acceleration vector
- **StandardScaler** — Feature normalization

---

## Keywords

**Machine Learning:** deep learning, neural networks, CNN, RNN, GRU, transfer learning, computer vision, time series analysis, supervised learning, classification, feature engineering

**Technologies:** Python, TensorFlow, Keras, FastAPI, React, Streamlit, OpenCV, scikit-learn, NumPy, Pandas, Vite, REST API, ASGI, Uvicorn

**Application Domain:** animal behavior, emotion recognition, livestock monitoring, veterinary diagnostics, pet health, farm management, IoT sensors, accelerometer data, real-time monitoring, predictive analytics

**Animals:** dog, cat, horse, bird, cattle, calf, chicken, poultry, livestock, pet

**Health & Welfare:** disease detection, anomaly detection, health monitoring, behavioral analysis, pain detection, early warning system, welfare assessment

**Data Processing:** image processing, video analysis, audio analysis, sensor fusion, data augmentation, normalization, feature extraction

---

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check if port 8000 is available
netstat -an | grep 8000

# Install missing dependencies
pip install -r requirements.txt
```

**Frontend not loading:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Model not found error:**
```
FileNotFoundError: model.keras not found
```
→ Download model files and place in `backend/model/` directory

**CORS error:**
```
Access to fetch blocked by CORS policy
```
→ Ensure backend is running before starting frontend

**Dashboard not connecting:**
```
Backend offline — please contact support
```
→ Start backend first: `uvicorn main:app --port 8000`

---

## Roadmap

### Phase 1 (Current)
- ✅ Dog emotion recognition
- ✅ Calf behavior monitoring
- ✅ Eye infection detection (cats/dogs)
- ✅ Chicken fowlpox detection
- ✅ Bird droppings analysis
- ✅ REST API
- ✅ Web interface
- ✅ Real-time dashboard

### Phase 2 (Q2 2026)
- 🔜 Cat behavior classification
- 🔜 Horse pain detection
- 🔜 Dog vocalization analysis
- 🔜 Multi-language support

### Phase 3 (Q3 2026)
- 🔜 Skin disease detection
- 🔜 Eye disease detection
- 🔜 Fowlpox detection
- 🔜 Bird droppings analysis

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

This project was developed as part of the **Artificial Intelligence and Machine Learning** curriculum at **Esprit School of Engineering**.

**Special Thanks:**
- **AcTBeCalf Dataset** — Calf behavior training data
- **TensorFlow Team** — Deep learning framework
- **FastAPI Community** — Web framework
- **Streamlit Team** — Dashboard framework
- **Open Source Community** — Libraries and tools

**Academic Supervision:**
- Esprit School of Engineering
- AI & ML Department

---

## Contact

**Project Team:** AniMind Development Team  
**Institution:** Esprit School of Engineering  
**Email:** [animind@gmail.com]  
**GitHub:** [https://github.com/your-username/animind](https://github.com/your-username/animind)

---

## Citation

If you use this project in your research, please cite:

```bibtex
@software{animind2026,
  title={AniMind: AI-Powered Animal Behavior Analysis Platform},
  author={Your Name},
  year={2026},
  institution={Esprit School of Engineering},
  url={https://github.com/your-username/animind}
}
```


