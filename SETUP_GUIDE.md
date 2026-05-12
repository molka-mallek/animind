# AniMind Project Setup Guide

This guide provides step-by-step instructions to set up and run the AniMind project with a Python virtual environment for the backend and the React frontend.

---

## Prerequisites

- **Python 3.9+** installed
- **Node.js 16+** and **npm** installed
- **Git** (optional, for version control)

---

## Project Structure

```
animind/
├── backend/          # FastAPI Python backend
├── frontend/         # React + Vite frontend
└── SETUP_GUIDE.md    # This file
```

---

## Part 1: Backend Setup (Python + FastAPI)

### Step 1: Navigate to Backend Directory

Open a terminal and navigate to the backend folder:

```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend
```

### Step 2: Create Virtual Environment

Create a Python virtual environment named `venv`:

```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment

Activate the virtual environment:

**For Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**For Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Note:** If you get a PowerShell execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the beginning of your command prompt.

### Step 4: Install Python Dependencies

With the virtual environment activated, install all required packages:

```cmd
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- PyTorch (deep learning)
- TensorFlow/Keras (AI models)
- OpenCV (computer vision)
- Streamlit (dashboard)
- And other dependencies

**Note:** This may take 5-10 minutes depending on your internet speed.

### Step 5: Download Required Model Files

⚠️ **IMPORTANT:** Some model files are too large for Git and must be downloaded separately.

**Required Downloads:**

1. **Dog Emotion Model:**
   - Download from: https://drive.google.com/file/d/15Zh-ydHIT5wkYkUiWmHzCXhz1pB4JXmy/view?usp=sharing
   - Save as: `backend/model/dog_emotion_best_model.keras`

2. **Skin Anomaly Models:**
   - Download from: https://drive.google.com/drive/folders/1Qa04B8OLaRj0VUHr9s5p7CVlVjYL_lEF?usp=sharing
   - Extract and place these files in `backend/model/`:
     - `best_classifier.h5`
     - `best_anomaly_detector.h5`
     - `unet_segmentation.h5`

**File structure after download:**
```
backend/model/
├── dog_emotion_best_model.keras       # Download this
├── best_classifier.h5                 # Download this
├── best_anomaly_detector.h5           # Download this
├── unet_segmentation.h5               # Download this
├── skin_anomaly_metadata.json         # Already in repo
└── calf_behavior/
    ├── label_encoder.pkl              # Already in repo
    ├── model_metadata.json            # Already in repo
    └── scaler.pkl                     # Already in repo
```

### Step 6: Run the Backend API

With the virtual environment still activated, start the FastAPI server:

```cmd
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access the API:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Keep this terminal open** — the backend must stay running.

---

## Part 2: Frontend Setup (React + Vite)

### Step 1: Open a NEW Terminal

Open a **second terminal window** (keep the backend terminal running).

### Step 2: Navigate to Frontend Directory

```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\frontend
```

### Step 3: Install Node Dependencies

Install all required npm packages:

```cmd
npm install
```

This will install:
- React 19
- React Router
- Vite (build tool)
- ESLint (linting)

**Note:** This may take 2-5 minutes.

### Step 4: Run the Frontend Development Server

Start the Vite development server:

```cmd
npm run dev
```

**Expected output:**
```
  VITE v8.0.4  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Access the frontend:**
- Web App: http://localhost:5173

**Keep this terminal open** — the frontend must stay running.

---

## Part 3: Dashboard Setup (Optional - Streamlit)

The Streamlit dashboard is for real-time calf behavior monitoring.

### Step 1: Open a THIRD Terminal

Open a **third terminal window** (keep backend and frontend running).

### Step 2: Navigate to Backend Directory

```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend
```

### Step 3: Activate Virtual Environment

Activate the same virtual environment:

**For Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**For Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

### Step 4: Run the Streamlit Dashboard

```cmd
streamlit run calf_dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Access the dashboard:**
- Dashboard: http://localhost:8501

**Keep this terminal open** — the dashboard must stay running.

---

## Summary: Running All Services

You need **3 terminal windows** running simultaneously:

### Terminal 1 - Backend API (Port 8000)
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend
venv\Scripts\activate.bat
uvicorn main:app --reload --port 8000
```

### Terminal 2 - Frontend Web App (Port 5173)
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\frontend
npm run dev
```

### Terminal 3 - Streamlit Dashboard (Port 8501) [Optional]
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend
venv\Scripts\activate.bat
streamlit run calf_dashboard.py
```

---

## Access Points

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Dashboard** | http://localhost:8501 | Calf behavior monitoring |

---

## Stopping the Services

To stop any service:
1. Go to the terminal window running that service
2. Press `CTRL + C`
3. Type `deactivate` (for backend/dashboard terminals) to exit the virtual environment

---

## Troubleshooting

### Backend Issues

**Problem: "python: command not found"**
- Solution: Make sure Python 3.9+ is installed and added to PATH

**Problem: "pip: command not found"**
- Solution: Use `python -m pip install -r requirements.txt` instead

**Problem: "Port 8000 is already in use"**
- Solution: Change the port: `uvicorn main:app --reload --port 8001`

**Problem: "ModuleNotFoundError: No module named 'fastapi'"**
- Solution: Make sure virtual environment is activated and dependencies are installed

**Problem: "FileNotFoundError: model.keras not found"**
- Solution: Download the required model files (see Step 5 in Backend Setup)

### Frontend Issues

**Problem: "npm: command not found"**
- Solution: Install Node.js from https://nodejs.org/

**Problem: "Port 5173 is already in use"**
- Solution: Vite will automatically use the next available port (5174, 5175, etc.)

**Problem: "CORS error in browser console"**
- Solution: Make sure the backend is running before starting the frontend

**Problem: "Failed to fetch" errors**
- Solution: Verify backend is running at http://localhost:8000

### Dashboard Issues

**Problem: "streamlit: command not found"**
- Solution: Make sure virtual environment is activated and streamlit is installed

**Problem: "Backend offline" message**
- Solution: Start the backend API first before running the dashboard

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Backend:** Changes to Python files automatically restart the server
- **Frontend:** Changes to React files automatically refresh the browser

### Deactivating Virtual Environment

When you're done working:
```cmd
deactivate
```

### Reactivating Virtual Environment

Next time you work on the project:
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend
venv\Scripts\activate.bat
```

---

## Quick Start Commands (Copy-Paste Ready)

### Backend
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend && venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000
```

### Frontend
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\frontend && npm run dev
```

### Dashboard
```cmd
cd c:\Users\Achre\Downloads\Animind_integration_finale-12.05\animind\backend && venv\Scripts\activate.bat && streamlit run calf_dashboard.py
```

---

## Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Download model files
4. ✅ Start backend API
5. ✅ Start frontend
6. ✅ (Optional) Start dashboard
7. 🎉 Start using AniMind!

---

## Need Help?

- Check the main README.md for feature documentation
- Visit http://localhost:8000/docs for API documentation
- Check browser console (F12) for frontend errors
- Check terminal output for backend errors

---

**Happy Coding! 🐾**
