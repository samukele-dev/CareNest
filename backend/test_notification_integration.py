# test_notification_integration_fixed.py
import requests
import json
import random
import string
import time

BASE_URL = "http://localhost:8000/api"

def generate_random_email():
    random_id = ''.join(random.choices(string.digits, k=8))
    return f"test_{random_id}@example.com"

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def test_messaging_notification_integration():
    print_section("TESTING MESSAGING-NOTIFICATION INTEGRATION")
    
    # Step 1: Create two users
    print("1. Creating two test users...")
    
    # User 1 (Client)
    email1 = generate_random_email()
    password = "Testpass123!"
    
    # Register User 1
    register_data1 = {
        "email": email1,
        "password1": password,
        "password2": password,
        "username": email1.split('@')[0],
        "user_type": "client",
        "terms_accepted": True,
        "first_name": "Client",
        "last_name": "Test"
    }
    
    response = requests.post(BASE_URL + "/auth/registration/", json=register_data1)
    if response.status_code != 201:
        print(f"✗ Failed to create user 1: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    print(f"✓ User 1 (Client) created: {email1}")
    
    # Login User 1
    login_data1 = {"email": email1, "password": password}
    response = requests.post(BASE_URL + "/auth/login/", json=login_data1)
    if response.status_code != 200:
        print(f"✗ Failed to login user 1: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    user1_data = response.json()
    token1 = user1_data['access']
    user1_id = user1_data['user']['id']
    headers1 = {'Authorization': f'Bearer {token1}'}
    
    print(f"  User 1 ID: {user1_id}, Token: {token1[:20]}...")
    
    # User 2 (Caregiver)
    email2 = generate_random_email()
    
    # Register User 2
    register_data2 = {
        "email": email2,
        "password1": password,
        "password2": password,
        "username": email2.split('@')[0],
        "user_type": "caregiver",
        "terms_accepted": True,
        "first_name": "Caregiver",
        "last_name": "Test"
    }
    
    response = requests.post(BASE_URL + "/auth/registration/", json=register_data2)
    if response.status_code != 201:
        print(f"✗ Failed to create user 2: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    print(f"✓ User 2 (Caregiver) created: {email2}")
    
    # Login User 2
    login_data2 = {"email": email2, "password": password}
    response = requests.post(BASE_URL + "/auth/login/", json=login_data2)
    if response.status_code != 200:
        print(f"✗ Failed to login user 2: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    user2_data = response.json()
    token2 = user2_data['access']
    user2_id = user2_data['user']['id']
    headers2 = {'Authorization': f'Bearer {token2}'}
    
    print(f"  User 2 ID: {user2_id}, Token: {token2[:20]}...")
    
    # Step 2: Start a conversation
    print("\n2. Starting conversation between users...")
    
    # Use the correct endpoint
    conv_url = BASE_URL + "/messaging/start-conversation/"
    conv_data = {"recipient_id": user2_id}
    
    response = requests.post(conv_url, json=conv_data, headers=headers1, timeout=5)
    if response.status_code not in [200, 201]:
        print(f"✗ Failed to start conversation: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    conversation = response.json()
    conversation_id = conversation.get('id')
    print(f"✓ Conversation created: ID={conversation_id}")
    
    # Step 3: Check initial notifications
    print("\n3. Checking initial notification counts...")
    
    # Check User 1 notifications
    response = requests.get(BASE_URL + "/notifications/notifications/", headers=headers1)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            user1_initial = len(data['results'])
        else:
            user1_initial = 0
        print(f"  User 1 initial notifications: {user1_initial}")
    
    # Check User 2 notifications
    response = requests.get(BASE_URL + "/notifications/notifications/", headers=headers2)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            user2_initial = len(data['results'])
        else:
            user2_initial = 0
        print(f"  User 2 initial notifications: {user2_initial}")
    
    # Step 4: Send a message from User 1 to User 2
    print("\n4. Sending message (should trigger notification)...")
    print("   Check Django console for: '✓ Notification sent to ...'")
    
    # *** CRITICAL: Let's debug what parameters your API actually accepts ***
    print("\n  DEBUG: Testing different parameter names...")
    
    # Based on your error, the API says it expects "recipient_id" or "conversation_id"
    # But let's test ALL possibilities
    
    test_cases = [
        # Test what your error message says
        {"content": "Test with conversation_id", "conversation_id": conversation_id},
        {"content": "Test with recipient_id", "recipient_id": user2_id},
        # Test what might actually work based on serializer
        {"content": "Test with conversation", "conversation": conversation_id},
        {"content": "Test with recipient", "recipient": user2_id},
    ]
    
    message_url = BASE_URL + "/messaging/messages/"
    successful_payload = None
    
    for i, test_payload in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {list(test_payload.keys())}")
        print(f"    Payload: {test_payload}")
        
        response = requests.post(message_url, json=test_payload, headers=headers1, timeout=5)
        
        if response.status_code in [200, 201]:
            print(f"    ✓ SUCCESS! Status: {response.status_code}")
            successful_payload = test_payload
            message_data = response.json()
            print(f"    Message ID: {message_data.get('id')}")
            break
        else:
            print(f"    ✗ Failed: {response.status_code}")
            if response.status_code == 500:
                print(f"    Server error - check Django console")
            else:
                print(f"    Error: {response.text[:100]}...")
    
    if not successful_payload:
        print(f"\n✗ All message sending attempts failed")
        print(f"\n  Your Django views.py has these errors:")
        print(f"  1. Line ~100: MultipleObjectsReturned - duplicate conversations")
        print(f"  2. Line ~120: UnboundLocalError - 'recipient' variable not defined")
        
        # Test direct notification instead
        test_direct_notification(headers1, user2_id, email1, email2)
        return
    
    # If we got here, message was sent
    print(f"\n✓ Message sent successfully with payload: {list(successful_payload.keys())}")
    
    # Wait for notification
    print("\n5. Waiting for notification to be processed...")
    time.sleep(2)
    
    # Step 5: Check if notification was created for User 2
    print("\n6. Checking if User 2 received notification...")
    
    response = requests.get(BASE_URL + "/notifications/notifications/", headers=headers2)
    if response.status_code == 200:
        data = response.json()
        
        # Parse notifications
        if isinstance(data, dict) and 'results' in data:
            notifications = data['results']
            user2_new = len(notifications)
        elif isinstance(data, list):
            notifications = data
            user2_new = len(notifications)
        else:
            notifications = []
            user2_new = 0
        
        print(f"  User 2 now has {user2_new} notifications")
        
        if user2_new > user2_initial:
            new_count = user2_new - user2_initial
            print(f"  ✓ User 2 received {new_count} new notification(s)!")
            
            # Show new notifications
            new_notifications = notifications[:new_count]
            for i, notif in enumerate(new_notifications):
                print(f"\n    Notification {i+1}:")
                print(f"      Type: {notif.get('notification_type', 'N/A')}")
                print(f"      Title: {notif.get('title', 'No title')}")
                print(f"      Message: {notif.get('message', 'No message')[:60]}...")
                print(f"      Read: {notif.get('is_read', 'N/A')}")
                
                if notif.get('notification_type') == 'message':
                    print(f"      ✓ This is a MESSAGE notification - INTEGRATION WORKING!")
                else:
                    print(f"      ⚠️  Not a message notification (type: {notif.get('notification_type')})")
        else:
            print(f"  ✗ User 2 did not receive new notifications")
            print(f"\n  Check if NotificationService is being called in messaging/views.py")
    
    # Step 6: Check if User 1 got any notifications (should not)
    print("\n7. Checking User 1 notifications (should be unchanged)...")
    
    response = requests.get(BASE_URL + "/notifications/notifications/", headers=headers1)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            user1_new = len(data['results'])
        else:
            user1_new = 0
        
        print(f"  User 1 now has {user1_new} notifications")
        if user1_new == user1_initial:
            print(f"  ✓ Correct: User 1 (sender) didn't get a notification")
        else:
            print(f"  ⚠️  User 1 got {user1_new - user1_initial} new notifications")
    
    print_section("TEST COMPLETE")
    
    print("\n📋 Summary:")
    print("  1. User registration: ✓ Working")
    print("  2. Conversation creation: ✓ Working")
    print("  3. Message sending: ✓ Working (with correct parameters)")
    print("  4. Notification creation: " + ("✓ Working" if 'user2_new' in locals() and user2_new > user2_initial else "✗ Not triggered"))
    
    if successful_payload:
        print(f"\n✅ CORRECT PARAMETER FORMAT:")
        print(f"   Use: {successful_payload}")

def test_direct_notification(headers, user2_id, email1, email2):
    """Test direct notification creation"""
    print("\n" + "="*60)
    print("TESTING DIRECT NOTIFICATION CREATION")
    print("="*60)
    
    notification_data = {
        "title": f"Test message from {email1}",
        "message": f"This simulates a message notification from {email1} to {email2}",
        "type": "message",
        "user_id": user2_id
    }
    
    response = requests.post(
        BASE_URL + "/notifications/create/",
        json=notification_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✓ Direct notification created!")
        notification = response.json()
        print(f"  Notification ID: {notification.get('id')}")
        print(f"  Type: {notification.get('notification_type')}")
        print(f"  Title: {notification.get('title')}")
    else:
        print(f"✗ Direct notification failed: {response.status_code}")

def check_message_payload():
    """Check the correct message payload format"""
    print("\n" + "="*60)
    print("MESSAGE PAYLOAD FORMAT CHECK")
    print("="*60)
    
    print("\n🚨 FIRST FIX YOUR DJANGO CODE:")
    print("\nYour messaging/views.py has TWO critical errors:")
    print("1. Line ~100: MultipleObjectsReturned - get() returned more than one Conversation")
    print("   Fix: You have duplicate conversations. Check your Conversation model's get_or_create logic.")
    print("\n2. Line ~120: UnboundLocalError - 'recipient' variable not defined")
    print("   Fix: Make sure 'recipient' is defined before using it in NotificationService.")
    
    print("\n🔧 Quick fixes needed in messaging/views.py:")
    print("1. Fix the get_or_create() to handle duplicates")
    print("2. Ensure 'recipient' variable is properly set before line 120")
    print("3. Check your MessageSerializer to see what field names it expects")

if __name__ == "__main__":
    print("Messaging-Notification Integration Test")
    print("Testing with correct payload format")
    print()
    
    test_messaging_notification_integration()
    
    # Show payload format help
    check_message_payload()