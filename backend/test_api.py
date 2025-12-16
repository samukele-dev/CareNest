import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def wait_for_server(timeout=30):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=2)
            if response.status_code < 500:  # Any non-server-error response
                print("✓ Server is running!")
                return True
        except requests.exceptions.ConnectionError:
            print(".", end="", flush=True)
            time.sleep(1)
        except requests.exceptions.RequestException:
            time.sleep(1)
    
    print(f"\n✗ Server not responding after {timeout} seconds")
    print("Make sure to run: python manage.py runserver")
    return False

def test_endpoints():
    print("Testing CareNest API...")
    
    # Wait for server
    if not wait_for_server():
        return
    
    # 1. Check API docs
    try:
        response = requests.get(f"{BASE_URL}/docs/", timeout=5)
        print(f"✓ API Docs: {response.status_code}")
    except Exception as e:
        print(f"✗ API Docs error: {e}")
    
    # 2. Test registration
    import random
    test_email = f"test_{random.randint(1000, 9999)}@example.com"
    test_user = {
        "email": test_email,
        "password1": "TestPass123!",
        "password2": "TestPass123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/registration/", 
            json=test_user,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ User registration successful for {test_email}")
            data = response.json()
            print(f"Response data: {data}")
            
            if 'access' in data:
                token = data['access']
                print(f"Token: {token[:50]}...")
                
                # 3. Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{BASE_URL}/auth/user/", 
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✓ Authenticated user endpoint works")
                    user_data = response.json()
                    print(f"  User ID: {user_data.get('id')}")
                    print(f"  Email: {user_data.get('email')}")
                else:
                    print(f"✗ Auth user failed: {response.status_code}")
                    
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ Registration error: {e}")

if __name__ == "__main__":
    test_endpoints()