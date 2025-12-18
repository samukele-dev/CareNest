# test_notifications_fixed.py
import requests
import json
import random
import string
import sys

BASE_URL = "http://localhost:8000/api"

def generate_random_email():
    """Generate random email for testing"""
    random_id = ''.join(random.choices(string.digits, k=8))
    return f"test_{random_id}@example.com"

def register_user_correct(email, password="Testpass123!", user_type="client"):
    """Register a user with correct fields for your setup"""
    
    url = BASE_URL + "/auth/registration/"
    
    # Based on error message, you need: user_type and terms_accepted
    data = {
        "email": email,
        "password1": password,
        "password2": password,
        "username": email.split('@')[0],
        "user_type": user_type,
        "terms_accepted": True,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        print(f"  Registering {email} as {user_type}...")
        response = requests.post(url, json=data, timeout=5)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"    ✓ Registration successful!")
            print(f"    Note: Check console for email confirmation")
            return response.json()
        else:
            print(f"    ✗ Registration failed: {response.status_code}")
            if response.status_code == 400:
                errors = response.json()
                print(f"    Errors: {errors}")
            return None
    except Exception as e:
        print(f"    Error: {e}")
        return None

def login_with_credentials(email, password="Testpass123!"):
    """Login with specific credentials"""
    
    url = BASE_URL + "/auth/login/"
    
    # Try different credential formats
    attempts = [
        {"email": email, "password": password},
        {"username": email, "password": password},
        {"email": email.split('@')[0], "password": password},
    ]
    
    for credentials in attempts:
        try:
            print(f"  Trying login with {list(credentials.keys())}...")
            response = requests.post(url, json=credentials, timeout=5)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✓ Login successful!")
                print(f"    Response keys: {list(data.keys())}")
                
                # Try to extract token
                token = None
                if 'access' in data:
                    token = data['access']
                    print(f"    Found token in 'access' field")
                elif 'access_token' in data:
                    token = data['access_token']
                    print(f"    Found token in 'access_token' field")
                elif 'key' in data:
                    token = data['key']
                    print(f"    Found token in 'key' field")
                elif 'token' in data:
                    token = data['token']
                    print(f"    Found token in 'token' field")
                
                if token:
                    print(f"    Token: {token[:30]}...")
                    
                    # Get user ID
                    user_id = None
                    if 'user' in data:
                        user_id = data['user'].get('id')
                    elif 'user_id' in data:
                        user_id = data['user_id']
                    elif 'pk' in data:
                        user_id = data['pk']
                    
                    return token, user_id, data
                else:
                    print(f"    ✗ No token found in response")
                    print(f"    Full response: {data}")
        except Exception as e:
            print(f"    Error: {e}")
    
    return None, None, None

def get_user_info(token):
    """Get user info using token"""
    
    # Try different user info endpoints
    endpoints = [
        "/auth/user/",
        "/users/profile/",
        "/users/me/",
        "/auth/me/",
    ]
    
    # Try with Bearer
    headers = {'Authorization': f'Bearer {token}'}
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                print(f"    User info from {endpoint}: {response.status_code}")
                return response.json()
        except:
            continue
    
    # Try with Token prefix
    headers = {'Authorization': f'Token {token}'}
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                print(f"    User info from {endpoint} (Token): {response.status_code}")
                return response.json()
        except:
            continue
    
    return None

def test_notifications_simple():
    """Simple test to check notifications setup"""
    
    print("="*70)
    print("SIMPLE NOTIFICATIONS TEST")
    print("="*70)
    
    # Step 1: Create a new user
    print("\n1. Creating a new test user...")
    email = generate_random_email()
    password = "Testpass123!"
    
    register_result = register_user_correct(email, password, "client")
    
    if not register_result:
        print("✗ Could not create user")
        return
    
    # Step 2: Login with the new user
    print("\n2. Logging in with new user...")
    token, user_id, auth_data = login_with_credentials(email, password)
    
    if not token:
        print("✗ Could not login with new user")
        print("\nTrying alternative login methods...")
        
        # Try with username instead of email
        username = email.split('@')[0]
        token, user_id, auth_data = login_with_credentials(username, password)
        
        if not token:
            print("✗ All login attempts failed")
            print("\nPossible issues:")
            print("1. Email confirmation required (check Django console)")
            print("2. Wrong password format")
            print("3. Authentication backend issue")
            return
    
    print(f"\n✓ Successfully authenticated!")
    print(f"  User ID: {user_id}")
    print(f"  Token: {token[:30]}...")
    
    # Get user info to verify
    user_info = get_user_info(token)
    if user_info:
        print(f"  User Info: ID={user_info.get('id')}, Email={user_info.get('email')}")
        if not user_id:
            user_id = user_info.get('id')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 3: Test notifications endpoints
    print("\n3. Testing notifications endpoints...")
    
    # Check if notifications app is accessible
    endpoints_to_test = [
        "/notifications/notifications/",
        "/notifications/",
        "/notifications/test/",
        "/notifications/create/",
        "/notifications/preferences/",
    ]
    
    for endpoint in endpoints_to_test:
        url = BASE_URL + endpoint
        print(f"\n  Testing {endpoint}")
        
        # Try GET first for list endpoints
        if endpoint in ["/notifications/notifications/", "/notifications/", "/notifications/preferences/"]:
            try:
                response = requests.get(url, headers=headers, timeout=3)
                print(f"    GET: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✓ Accessible")
                    
                    if isinstance(data, dict):
                        if 'results' in data:
                            count = len(data['results'])
                            total = data.get('count', count)
                            print(f"    Found {total} items (paginated)")
                        else:
                            print(f"    Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"    Found {len(data)} items")
            except Exception as e:
                print(f"    Error: {e}")
        
        # Try POST for test/create endpoints
        elif endpoint in ["/notifications/test/", "/notifications/create/"]:
            try:
                if endpoint == "/notifications/test/":
                    response = requests.post(url, headers=headers, timeout=3)
                else:
                    test_data = {"title": "Test", "message": "Test notification", "type": "system"}
                    response = requests.post(url, json=test_data, headers=headers, timeout=3)
                
                print(f"    POST: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"    ✓ Works!")
            except Exception as e:
                print(f"    Error: {e}")
    
    # Step 4: Quick setup check
    print("\n4. Setup verification...")
    
    # Check if we can access any notifications endpoint
    test_url = BASE_URL + "/notifications/notifications/"
    try:
        response = requests.get(test_url, headers=headers, timeout=3)
        if response.status_code == 200:
            print("✓ Notifications API is accessible")
            
            # Try to create a notification
            create_url = BASE_URL + "/notifications/create/"
            test_data = {
                "title": "Setup Test",
                "message": "Testing if notifications work",
                "type": "system"
            }
            
            response = requests.post(create_url, json=test_data, headers=headers, timeout=3)
            if response.status_code == 201:
                print("✓ Can create notifications via API")
            elif response.status_code == 404:
                print("✗ Create endpoint not found (check URLs)")
            else:
                print(f"✗ Create failed: {response.status_code}")
        else:
            print(f"✗ Notifications endpoint: {response.status_code}")
            print("  Make sure:")
            print("  1. Notifications app is in INSTALLED_APPS")
            print("  2. You've run: python manage.py migrate notifications")
            print("  3. URLs are configured in urls.py")
    except Exception as e:
        print(f"✗ Error accessing notifications: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    

def quick_setup_check():
    """Quick check if notifications is set up"""
    print("\nQuick Setup Check:")
    print("-" * 40)
    
    # Check with a simple request
    try:
        # First create a user
        email = generate_random_email()
        print(f"Creating test user: {email}")
        
        register_data = {
            "email": email,
            "password1": "Testpass123!",
            "password2": "Testpass123!",
            "username": email.split('@')[0],
            "user_type": "client",
            "terms_accepted": True,
        }
        
        response = requests.post(BASE_URL + "/auth/registration/", json=register_data, timeout=5)
        if response.status_code == 201:
            print("✓ Test user created")
            
            # Try to login
            login_data = {"email": email, "password": "Testpass123!"}
            response = requests.post(BASE_URL + "/auth/login/", json=login_data, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access')
                
                if token:
                    print("✓ Got authentication token")
                    
                    # Try notifications endpoint
                    headers = {'Authorization': f'Bearer {token}'}
                    response = requests.get(BASE_URL + "/notifications/notifications/", headers=headers, timeout=3)
                    
                    if response.status_code == 200:
                        print("✓ Notifications endpoint accessible!")
                        return True
                    else:
                        print(f"✗ Notifications endpoint: {response.status_code}")
                        return False
                else:
                    print("✗ No token in response")
                    return False
            else:
                print(f"✗ Login failed: {response.status_code}")
                return False
        else:
            print(f"✗ Registration failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("CareNest Notifications Test")
    print("-" * 50)
    
    # First do a quick check
    if quick_setup_check():
        print("\n✓ Basic setup looks good!")
        print("\nRunning full test...")
        test_notifications_simple()
    else:
        print("\n✗ Setup issues detected")
        print("\nRun these commands to set up notifications:")
        print("1. python manage.py makemigrations notifications")
        print("2. python manage.py migrate")
        print("3. Check notifications is in INSTALLED_APPS")
        print("4. Verify urls.py includes notifications URLs")
        print("\nThen run this test again.")