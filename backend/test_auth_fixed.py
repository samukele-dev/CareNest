import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_auth_correctly():
    print("Testing authentication with correct methods...")
    
    # 1. Register a user
    test_email = f"test_{int(time.time())}@example.com"
    user_data = {
        "email": test_email,
        "password1": "TestPass123!",
        "password2": "TestPass123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    print(f"Registering: {test_email}")
    response = requests.post(f"{BASE_URL}/auth/registration/", json=user_data)
    
    if response.status_code not in [200, 201]:
        print(f"Registration failed: {response.status_code}")
        print(response.json())
        return
    
    reg_data = response.json()
    print("✓ Registration successful")
    
    # 2. Login to get proper token (dj_rest_auth uses Token auth for /auth/ endpoints)
    print("\nLogging in...")
    login_data = {
        "email": test_email,
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return
    
    login_data = response.json()
    print("✓ Login successful")
    print(f"Response keys: {list(login_data.keys())}")
    
    # 3. Try ALL possible authentication methods for /auth/user/
    
    # Method A: JWT Token (Bearer)
    if 'access' in login_data:
        print("\nTrying JWT Bearer token...")
        headers = {"Authorization": f"Bearer {login_data['access']}"}
        response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Success with JWT Bearer!")
            print(f"  User: {response.json()}")
            return headers
    
    # Method B: Plain token (no prefix)
    if 'key' in login_data:
        print("\nTrying plain token (key)...")
        headers = {"Authorization": f"Token {login_data['key']}"}
        response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Success with plain Token!")
            print(f"  User: {response.json()}")
            return headers
    
    # Method C: Check what dj_rest_auth actually expects
    print("\nChecking available auth endpoints...")
    response = requests.get(f"{BASE_URL}/auth/")
    if response.status_code == 200:
        print(f"Available endpoints: {response.json()}")
    
    # Method D: Try session auth (via cookies)
    print("\nTrying with session (cookies)...")
    session = requests.Session()
    response = session.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        response = session.get(f"{BASE_URL}/auth/user/")
        print(f"  Status with session: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Success with session cookies!")
            print(f"  User: {response.json()}")
            return {"session": "cookies"}
    
    print("\n✗ All methods failed")
    print("\nCurrent login response:")
    print(json.dumps(login_data, indent=2))
    
    return None

def test_custom_endpoint():
    """Test if our custom user endpoint works with JWT"""
    print("\n" + "="*50)
    print("Testing CUSTOM user endpoint (/api/users/profile/)...")
    
    # 1. Register and get JWT token
    test_email = f"custom_{int(time.time())}@example.com"
    user_data = {
        "email": test_email,
        "password1": "CustomPass123!",
        "password2": "CustomPass123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=user_data)
    
    if response.status_code not in [200, 201]:
        print(f"Registration failed: {response.status_code}")
        return
    
    data = response.json()
    token = data.get('access')
    
    if token:
        print(f"✓ Got JWT token: {token[:50]}...")
        
        # Test our custom endpoint with JWT
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
        
        print(f"Custom endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Custom endpoint works with JWT!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Custom endpoint failed: {response.text[:200]}")
    else:
        print("✗ No token in response")

if __name__ == "__main__":
    # Test the dj_rest_auth endpoints
    test_auth_correctly()
    
    # Test our custom endpoint
    test_custom_endpoint()