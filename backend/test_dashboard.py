"""
test_dashboard.py — Quick test script for the calf monitoring system

Run this to verify:
1. Backend is running
2. Model files are loaded correctly
3. API endpoints work as expected
"""

import requests
import time

BACKEND_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is online."""
    print("Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        if response.status_code == 200:
            print("✓ Backend is online")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend is offline")
        print("  Start it with: uvicorn main:app --port 8000")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_predict_endpoint():
    """Test the /predict-calf endpoint with simulated data."""
    print("\nTesting /predict-calf endpoint...")
    
    # Simulate 100 readings to fill the buffer
    calf_id = "test_calf"
    
    for i in range(105):
        # Generate simulated "lying" behavior
        accX = 0.95 + (i * 0.001)  # slight variation
        accY = -0.10
        accZ = 0.05
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/predict-calf",
                json={"id": calf_id, "accX": accX, "accY": accY, "accZ": accZ},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'warming_up':
                    progress = result.get('progress', 0)
                    required = result.get('required', 100)
                    print(f"  Warming up... {progress}/{required}")
                
                elif result.get('status') == 'success':
                    res_data = result['result']
                    behavior = res_data['behavior']
                    confidence = res_data['confidence']
                    print(f"✓ Prediction successful!")
                    print(f"  Behavior: {behavior}")
                    print(f"  Confidence: {confidence:.2%}")
                    print(f"  Alert: {res_data.get('alert', False)}")
                    print(f"  Event: {res_data.get('event', {}).get('type', 'none')}")
                    
                    # Show top 3 probabilities
                    probs = res_data.get('probabilities', {})
                    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"  Top 3 probabilities:")
                    for cls, prob in sorted_probs:
                        print(f"    {cls}: {prob:.2%}")
                    
                    return True
                
                else:
                    print(f"  Unexpected status: {result.get('status')}")
            
            else:
                print(f"✗ Request failed with status {response.status_code}")
                return False
        
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
        
        time.sleep(0.01)  # Small delay between readings
    
    return False

def test_list_calves():
    """Test the /calves endpoint."""
    print("\nTesting /calves endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/calves", timeout=2)
        if response.status_code == 200:
            calves = response.json().get('calves', [])
            print(f"✓ Active calves: {calves}")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("AniMind Calf Dashboard — System Test")
    print("=" * 60)
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n⚠️  Backend is not running. Start it first:")
        print("   cd backend")
        print("   uvicorn main:app --reload --port 8000")
        return
    
    # Test 2: List calves
    test_list_calves()
    
    # Test 3: Prediction endpoint
    test_predict_endpoint()
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)
    print("\nYou can now start the dashboard:")
    print("  streamlit run calf_dashboard.py")

if __name__ == "__main__":
    main()
