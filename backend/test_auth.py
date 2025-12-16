import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_all_auth_methods():
    """Test different authentication approaches"""
    print("Testing authentication methods...")
    
    # 1. Register a user
    test_email = f"auth_test_{int(time.time())}@example.com"
    user_data = {
        "email": test_email,
        "password1": "AuthTest123!",
        "password2": "AuthTest123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=user_data)
    
    if response.status_code not in [200, 201]:
        print(f"Registration failed: {response.status_code}")
        print(response.json())
        return
    
    data = response.json()
    print(f"Registration response: {json.dumps(data, indent=2)}")
    
    # 2. Try different authentication headers
    token = data.get('access')
    refresh = data.get('refresh')
    key = data.get('key')  # Some APIs return 'key' instead of 'access'
    
    headers_to_try = []
    
    if token:
        headers_to_try.append(("Bearer Token", {"Authorization": f"Bearer {token}"}))
        headers_to_try.append(("JWT Token", {"Authorization": f"JWT {token}"}))
    
    if key:
        headers_to_try.append(("Token Key", {"Authorization": f"Token {key}"}))
    
    # 3. Test each header
    for header_name, headers in headers_to_try:
        print(f"\nTrying {header_name}...")
        try:
            response = requests.get(f"{BASE_URL}/auth/user/", headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success! User: {response.json().get('email')}")
                return headers  # Return successful headers
            else:
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 4. Try login endpoint to get correct token
    print("\nTrying login endpoint...")
    login_data = {
        "email": test_email,
        "password": "AuthTest123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            login_response = response.json()
            print(f"Login response: {json.dumps(login_response, indent=2)}")
            
            # Test with login token
            token = login_response.get('access') or login_response.get('token')
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
                print(f"User endpoint with login token: {response.status_code}")
                if response.status_code == 200:
                    print("✓ Authentication successful via login!")
                    return headers
    except Exception as e:
        print(f"Login error: {e}")
    
    return None

if __name__ == "__main__":
    successful_headers = test_all_auth_methods()
    if successful_headers:
        print(f"\n✓ Use these headers: {successful_headers}")
    else:
        print("\n✗ All authentication methods failed")