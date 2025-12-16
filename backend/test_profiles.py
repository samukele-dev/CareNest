import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_profiles():
    print("Testing Profile System...")
    
    # 1. Register a caregiver
    caregiver_email = f"caregiver_{int(time.time())}@example.com"
    reg_data = {
        "email": caregiver_email,
        "password1": "Caregiver123!",
        "password2": "Caregiver123!",
        "user_type": "caregiver",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=reg_data)
    if response.status_code not in [200, 201]:
        print(f"Caregiver registration failed: {response.status_code}")
        print(response.json())
        return
    
    caregiver_token = response.json()['access']
    print(f"✓ Caregiver registered: {caregiver_email}")
    
    # 2. Create caregiver profile
    profile_data = {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "gender": "female",
        "years_experience": 5,
        "hourly_rate": "25.00",
        "bio": "Experienced caregiver specializing in elderly care.",
        "skills": ["elderly_care", "medication_management", "mobility_assistance"],
        "certifications": ["CPR", "First Aid", "Caregiver Certification"],
        "languages": ["English", "Zulu"],
        "is_available": True,
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "available_times": "8am-6pm",
        "city": "Johannesburg",
        "suburb": "Sandton"
    }
    
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.put(
        f"{BASE_URL}/profiles/caregiver/",
        json=profile_data,
        headers=headers
    )
    
    print(f"Caregiver profile update: {response.status_code}")
    if response.status_code == 200:
        print("✓ Caregiver profile created successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Profile creation failed: {response.text[:200]}")
    
    # 3. Test public caregiver listing
    print("\nTesting public caregiver listing...")
    response = requests.get(f"{BASE_URL}/profiles/caregivers/")
    print(f"Public caregiver list status: {response.status_code}")
    if response.status_code == 200:
        caregivers = response.json()
        print(f"Found {len(caregivers)} caregivers")
        if caregivers:
            print(f"First caregiver: {caregivers[0]['first_name']} {caregivers[0]['last_name']}")
    
    # 4. Register a client
    client_email = f"client_{int(time.time())}@example.com"
    reg_data = {
        "email": client_email,
        "password1": "Client123!",
        "password2": "Client123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=reg_data)
    if response.status_code not in [200, 201]:
        print(f"Client registration failed: {response.status_code}")
        return
    
    client_token = response.json()['access']
    print(f"\n✓ Client registered: {client_email}")
    
    # 5. Create client profile
    client_profile = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+27123456789",
        "address": "123 Main Street, Sandton",
        "city": "Johannesburg",
        "care_type": "elderly",
        "special_requirements": "Needs assistance with medication and daily activities"
    }
    
    headers = {"Authorization": f"Bearer {client_token}"}
    response = requests.put(
        f"{BASE_URL}/profiles/client/",
        json=client_profile,
        headers=headers
    )
    
    print(f"Client profile update: {response.status_code}")
    if response.status_code == 200:
        print("✓ Client profile created successfully!")
        print(json.dumps(response.json(), indent=2))
    
    return caregiver_token, client_token

if __name__ == "__main__":
    test_profiles()