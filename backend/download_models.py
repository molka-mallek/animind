"""
Script to download AI model files from Google Drive
Run this after cloning the repository to get the required model files
"""

import os
import gdown
from pathlib import Path

# Model download links (Google Drive file IDs)
MODELS = {
    "dog_emotion_best_model.keras": "YOUR_GOOGLE_DRIVE_FILE_ID_HERE",
    "best_classifier.h5": "YOUR_GOOGLE_DRIVE_FILE_ID_HERE",
    "best_anomaly_detector.h5": "YOUR_GOOGLE_DRIVE_FILE_ID_HERE",
    "unet_segmentation.h5": "YOUR_GOOGLE_DRIVE_FILE_ID_HERE",
}

def download_model(filename, file_id):
    """Download a model file from Google Drive"""
    model_dir = Path(__file__).parent / "model"
    model_dir.mkdir(exist_ok=True)
    
    output_path = model_dir / filename
    
    if output_path.exists():
        print(f"✓ {filename} already exists, skipping...")
        return
    
    print(f"⬇️  Downloading {filename}...")
    url = f"https://drive.google.com/uc?id={file_id}"
    
    try:
        gdown.download(url, str(output_path), quiet=False)
        print(f"✅ {filename} downloaded successfully!")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

def main():
    print("=" * 60)
    print("AniMind Model Downloader")
    print("=" * 60)
    print()
    
    # Check if gdown is installed
    try:
        import gdown
    except ImportError:
        print("❌ gdown is not installed. Installing...")
        os.system("pip install gdown")
        import gdown
    
    # Download all models
    for filename, file_id in MODELS.items():
        if file_id == "YOUR_GOOGLE_DRIVE_FILE_ID_HERE":
            print(f"⚠️  Skipping {filename} - no download link configured")
            continue
        download_model(filename, file_id)
    
    print()
    print("=" * 60)
    print("✅ Model download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start the backend: uvicorn main:app --reload")
    print("2. Start the frontend: cd ../frontend && npm run dev")

if __name__ == "__main__":
    main()
