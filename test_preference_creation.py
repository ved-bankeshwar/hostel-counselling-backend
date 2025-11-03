"""
Test the preference creation endpoint with correct field mapping
"""
import requests

# Test data
base_url = "http://localhost:8000"

# Get a valid room ID first
print("1. Fetching available rooms...")
rooms_response = requests.get(f"{base_url}/api/rooms/available?floorNumber=1")
rooms_data = rooms_response.json()

if rooms_data["count"] > 0:
    room_id = rooms_data["data"][0]["id"]
    print(f"✓ Found room ID: {room_id}")
    
    # Test preference creation
    print("\n2. Testing preference creation...")
    preference_data = {
        "user_id": 301,
        "session_id": 1,
        "room_id": room_id,
        "priority": 1
    }
    
    print(f"Request body: {preference_data}")
    
    # Note: You'll need to add the Authorization header with a valid Firebase token
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_FIREBASE_TOKEN_HERE"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/preferences",
            json=preference_data,
            headers=headers
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Preference created successfully!")
        elif response.status_code == 422:
            print("\n❌ Validation Error - Check the field names and types:")
            print(response.json())
        elif response.status_code == 401:
            print("\n🔒 Authentication required - Add Authorization header")
        else:
            print(f"\n⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
else:
    print("❌ No available rooms found")

print("\n" + "="*80)
print("FIELD MAPPING REFERENCE:")
print("="*80)
print("Frontend sends (snake_case):")
print("  user_id, session_id, room_id, priority")
print("\nBackend converts to (camelCase):")
print("  userId, preferenceRank, roomId")
print("="*80)
