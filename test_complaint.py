import base64
import httpx
import json
import os

BASE_URL = "http://127.0.0.1:8002"

def test_raise_complaint():
    print("\n--- Testing /raise-complaint ---")
    
    # 1. Read and encode the local image
    image_path = os.path.join("..", "stalking.jpg")
    try:
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        print(f"Error: {image_path} not found.")
        return

    # 2. Prepare payload
    payload = {
        "user_id": "U123",
        "complaint_type": "Stalking",
        "image": img_base64,
        "text": "This person was stalking me near the bus stop"
    }

    # 3. Call the endpoint
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{BASE_URL}/raise-complaint", json=payload)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("Response JSON:")
                print(json.dumps(result, indent=2))
            else:
                print(f"Error Response: {response.text}")
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_raise_complaint()
