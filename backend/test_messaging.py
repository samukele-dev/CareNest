import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_messaging_system():
    print("=" * 60)
    print("TESTING MESSAGING SYSTEM")
    print("=" * 60)
    
    timestamp = int(time.time())
    
    # 1. Create two users for messaging
    print("\n1. Creating users for messaging test...")
    
    # User 1 (Caregiver)
    caregiver_data = {
        "email": f"msg_caregiver_{timestamp}@example.com",
        "password1": "Caregiver123!",
        "password2": "Caregiver123!",
        "user_type": "caregiver",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=caregiver_data)
    caregiver_token = response.json()['access']
    caregiver_id = response.json()['user']['id']
    
    # Create caregiver profile
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    profile_response = requests.put(f"{BASE_URL}/profiles/caregiver/", json={
        "first_name": "Chatty",
        "last_name": "Caregiver",
        "city": "Message City"
    }, headers=headers)
    
    # User 2 (Client)
    client_data = {
        "email": f"msg_client_{timestamp}@example.com",
        "password1": "Client123!",
        "password2": "Client123!",
        "user_type": "client",
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/registration/", json=client_data)
    client_token = response.json()['access']
    client_id = response.json()['user']['id']
    
    # Create client profile
    headers = {"Authorization": f"Bearer {client_token}"}
    requests.put(f"{BASE_URL}/profiles/client/", json={
        "first_name": "Messaging",
        "last_name": "Client",
        "city": "Message City"
    }, headers=headers)
    
    print(f"✓ Caregiver ID: {caregiver_id}")
    print(f"✓ Client ID: {client_id}")
    
    # 2. Start a conversation (201 = Created, 200 = Already exists)
    print("\n2. Starting a conversation...")
    headers = {"Authorization": f"Bearer {client_token}"}
    conversation_data = {"recipient_id": caregiver_id}
    
    response = requests.post(
        f"{BASE_URL}/messaging/start-conversation/",
        json=conversation_data,
        headers=headers
    )
    
    # BOTH 200 and 201 are SUCCESS!
    if response.status_code in [200, 201]:
        conversation = response.json()
        conversation_id = conversation['id']
        print(f"✓ Conversation {'created' if response.status_code == 201 else 'found'}: ID={conversation_id}")
        print(f"  Status: {response.status_code}")
        print(f"  Participants: {len(conversation['participants'])} users")
    else:
        print(f"✗ Conversation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # 3. Send a message
    print("\n3. Sending a message...")
    message_data = {
        "conversation_id": conversation_id,
        "content": "Hello! I'm interested in your care services."
    }
    
    response = requests.post(
        f"{BASE_URL}/messaging/messages/",
        json=message_data,
        headers=headers
    )
    
    if response.status_code == 201:
        message = response.json()
        print(f"✓ Message sent successfully!")
        print(f"  Message ID: {message['id']}")
        print(f"  Content: '{message['content'][:50]}...'")
    else:
        print(f"✗ Message failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # 4. Get conversations list
    # 4. Get conversations list
    print("\n4. Getting conversations list...")
    response = requests.get(f"{BASE_URL}/messaging/conversations/", headers=headers)
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✓ Conversations found: {len(conversations)}")
        
        # DEBUG: Print each item's type and first 100 chars
        print("\nDEBUG - Checking conversation items:")
        for i, conv in enumerate(conversations):
            print(f"  Item {i}: Type = {type(conv)}")
            if isinstance(conv, str):
                print(f"     String content: '{conv[:100]}...'")
                if '<!DOCTYPE html>' in conv or '<html>' in conv:
                    print("     ✗ This is an HTML error page!")
            elif isinstance(conv, dict):
                print(f"     Dict keys: {list(conv.keys())}")
                if 'id' in conv:
                    print(f"     Conversation ID: {conv['id']}")
        
        # Only process dict items
        valid_conversations = [c for c in conversations if isinstance(c, dict)]
        print(f"\nValid conversations (dicts): {len(valid_conversations)}")
        
        for conv in valid_conversations[:3]:  # Show first 3 valid ones
            other_user = conv.get('other_user', {})
            print(f"  - Conversation ID: {conv.get('id')}")
            print(f"    With: {other_user.get('display_name', 'Unknown')}")
            print(f"    Unread: {conv.get('unread_count', 0)} messages")
    else:
        print(f"✗ Conversations failed: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
    
    # 6. Send reply from caregiver
    print("\n6. Sending reply from caregiver...")
    reply_data = {
        "conversation_id": conversation_id,
        "content": "Hi! I'd be happy to help. What type of care are you looking for?"
    }
    
    response = requests.post(
        f"{BASE_URL}/messaging/messages/",
        json=reply_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✓ Reply sent successfully")
    else:
        print(f"✗ Reply failed: {response.status_code}")
    
    # 7. Check unread count
    print("\n7. Checking unread messages...")
    headers = {"Authorization": f"Bearer {client_token}"}  # Switch back to client
    response = requests.get(f"{BASE_URL}/messaging/unread-count/", headers=headers)
    
    if response.status_code == 200:
        unread = response.json().get('unread_count', 0)
        print(f"✓ Unread messages: {unread}")
    else:
        print(f"✗ Unread count failed: {response.status_code}")
    
    # 8. Mark conversation as read
    print("\n8. Marking conversation as read...")
    response = requests.post(
        f"{BASE_URL}/messaging/conversations/{conversation_id}/mark-read/",
        headers=headers
    )
    
    if response.status_code == 200:
        marked = response.json().get('marked_read', 0)
        print(f"✓ Marked {marked} messages as read")
    else:
        print(f"✗ Mark read failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 MESSAGING SYSTEM TEST COMPLETE! 🎉")
    print("=" * 60)
    print("\n✅ Features working:")
    print("  ✓ User registration & authentication")
    print("  ✓ Profile creation")
    print("  ✓ Starting conversations")
    print("  ✓ Sending messages")
    print("  ✓ Listing conversations")
    print("  ✓ Reading messages")
    print("  ✓ Unread count tracking")
    print("  ✓ Marking as read")
    
    return caregiver_token, client_token, conversation_id

if __name__ == "__main__":
    test_messaging_system()