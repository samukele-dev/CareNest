# discover_endpoints.py
import requests
import json

BASE_URL = "http://localhost:8000/api"

def discover_endpoints():
    print("Discovering available endpoints...")
    
    # Check common patterns
    endpoints = [
        "/", "/auth/", "/users/", "/profiles/", "/bookings/", 
        "/messages/", "/notifications/", "/reviews/"
    ]
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=3)
            print(f"\n{endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Response keys: {list(data.keys())}")
                except:
                    print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"\n{endpoint}: Error - {e}")
    
    # Try to find registration endpoint
    print("\n\nTrying to find registration endpoint...")
    register_endpoints = [
        "/auth/register/",
        "/users/register/", 
        "/register/",
        "/auth/signup/",
        "/users/signup/"
    ]
    
    for endpoint in register_endpoints:
        url = BASE_URL + endpoint
        try:
            response = requests.post(url, json={}, timeout=3)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"  Might be valid (got {response.status_code})")
        except:
            print(f"{endpoint}: Failed to connect")

if __name__ == "__main__":
    discover_endpoints()