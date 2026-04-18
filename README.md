# 🐾 AniMind

An AI-powered platform that helps pet owners and farmers understand animal behavior.
Upload a photo or video and get clear insights about how your animal feels.

---

## 📁 Project Structure

```
animind/
  frontend/       # React app (Vite)
  backend/        # Python API (FastAPI)
  .gitignore
  README.md
```

---

## ⚠️ Before You Start — Download the Model

The AI model file is not included in this repo (too large for git).

1. Download `dog_emotion_best_model.keras` from the shared link:
   > 📎 **[Insert Google Drive / HuggingFace link here]**

2. Place it here:
   ```
   backend/model/dog_emotion_best_model.keras
   ```

---

## 🚀 Running the Backend

Make sure you have **Python 3.9+** installed.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be running at: `http://127.0.0.1:8000`

To verify it works, open your browser and go to:
`http://127.0.0.1:8000` — you should see `{"message": "AniMind API is running"}`

---

## 💻 Running the Frontend

Make sure you have **Node.js 18+** installed.

```bash
cd frontend
npm install
npm run dev
```

The app will be running at: `http://localhost:5173`

---

## 🔁 Running Both Together

You need **two terminals open at the same time**:

| Terminal 1 (Backend)         | Terminal 2 (Frontend)  |
|------------------------------|------------------------|
| `cd backend`                 | `cd frontend`          |
| `uvicorn main:app --reload`  | `npm run dev`          |

Then open `http://localhost:5173` in your browser.

---

## 🧩 Available Features

| Feature | Status |
|---|---|
| Dog Emotion Analysis (photo + video) | ✅ Ready |
| Skin Disease Detection | 🔜 Coming soon |
| Rabies Detection | 🔜 Coming soon |
| Livestock Behavior Monitoring | 🔜 Coming soon |
| Wound Detection | 🔜 Coming soon |
| Breed Identification | 🔜 Coming soon |
| Activity & Vitals Tracker | 🔜 Coming soon |

---

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, React Router
- **Backend:** FastAPI, TensorFlow, OpenCV, Ultralytics YOLOv8
- **Model:** Custom-trained Keras model (5 emotion classes)

---

## ❓ Common Issues

**Model not found error on startup**
→ Make sure `dog_emotion_best_model.keras` is inside `backend/model/`

**CORS error in browser**
→ Make sure the backend is running before you use the frontend

**`uvicorn` not found**
→ Run `pip install uvicorn` or make sure your Python environment is activated

**`npm install` fails**
→ Make sure you're inside the `frontend/` folder when running it
