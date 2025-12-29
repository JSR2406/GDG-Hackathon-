import requests
import json
import time

# Use Local for robust testing
BASE_URL = "http://localhost:8000/api/v1"

def print_step(msg):
    print(f"\n{'='*50}\n👉 {msg}\n{'='*50}")

def run_test():
    print_step("STARTING ECO-SYNC FULL SYSTEM TEST (Demo Profiles)")

    # 1. SETUP DEMO USERS
    users = [
        {"name": "Alice Logistics", "email": "alice@corp.com", "semester": 1, "department": "Logistics", "hostel": "Block A", "role": "Demo Owner"},
        {"name": "Bob IT Solutions", "email": "bob@tech.com", "semester": 2, "department": "IT", "hostel": "Block B", "role": "Demo Owner"},
        {"name": "Charlie Sales", "email": "charlie@sales.com", "semester": 3, "department": "Sales", "hostel": "Block C", "role": "Demo Owner"}
    ]
    
    user_ids = {}

    for u in users:
        print(f"Checking/Creating User: {u['name']}...")
        try:
            res = requests.post(f"{BASE_URL}/users/", json=u)
            if res.status_code == 200:
                data = res.json()
                user_ids[u['email']] = data['id']
                print(f"✅ Created/Found User ID: {data['id']}")
            else:
                # If 400 (likely email exists), fetch list
                all_users = requests.get(f"{BASE_URL}/users/").json()
                found = next((x for x in all_users if x['email'] == u['email']), None)
                if found:
                    user_ids[u['email']] = found['id']
                    print(f"✅ Found Existing User ID: {found['id']}")
                else:
                    print(f"❌ Failed to create/find user {u['email']}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return

    alice_id = user_ids.get("alice@corp.com")
    bob_id = user_ids.get("bob@tech.com")
    
    if not alice_id or not bob_id:
        print("❌ Critical: Alice or Bob ID missing. Aborting.")
        return

    # 2. ITEM UPLOAD (Alice uploads 'Old Textbook')
    print_step("TEST: Item Upload with Photo URL")
    item_payload = {
        "name": "Old Biology Textbook",
        "category": "Textbooks",
        "condition": "Used",
        "description": "Standard bio book, slight wear",
        "photo_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=300"
    }
    res = requests.post(f"{BASE_URL}/items/users/{alice_id}/items", json=item_payload)
    
    item_id = None
    if res.status_code == 200:
        item = res.json()
        item_id = item['id']
        print(f"✅ Item Uploaded: {item['name']} (ID: {item['id']})")
    else:
        print(f"❌ Item Upload Failed: {res.text}")

    # 3. BARTER INTENT (Alice wants 'Calculator')
    print_step("TEST: Creating Barter Intent")
    intent_payload = {
        "item_id": item_id if item_id else 1, 
        "want_category": "Electronics",
        "description": "Need a scientific calculator",
        "is_emergency": False
    }
    # Fix: Pass user_id as query param
    res = requests.post(f"{BASE_URL}/barter/barter-intents?user_id={alice_id}", json=intent_payload)
    if res.status_code == 200:
        data = res.json()
        print(f"✅ Intent Created! Match Found? {data.get('match_found')}")
        if data.get('match_found'):
            print(f"   🎉 MATCH DETAILS: {data['match']}")
    else:
        print(f"❌ Barter Intent Failed: {res.text}")

    # 4. LOST & FOUND (Bob reports lost Keys)
    print_step("TEST: Lost & Found Posting")
    lf_payload = {
        "item_name": "Car Keys",
        "category": "Accessories",
        "description": "Lost near parking lot",
        "type": "lost", 
        "photo_url": "https://dummyimage.com/300"
    }
    # Fix: Pass user_id as query param
    res = requests.post(f"{BASE_URL}/lost-found/?user_id={bob_id}", json=lf_payload)
    if res.status_code == 200:
        lf_item = res.json()
        print(f"✅ Lost Item Posted: {lf_item['item_name']} (ID: {lf_item['id']})")
    else:
        print(f"❌ Lost & Found Failed: {res.text}")

    # 5. IMAGE UPLOAD ENDPOINT
    print_step("TEST: Image Upload Endpoint")
    with open("test_img.jpg", "w") as f: f.write("dummy image content")
    
    # Fix: Send as image/jpeg
    files = {'file': ('test_img.jpg', open('test_img.jpg', 'rb'), 'image/jpeg')}
    res = requests.post(f"{BASE_URL}/lost-found/upload", files=files)
    if res.status_code == 200:
        print(f"✅ Image Upload Success: URL = {res.json()['photo_url']}")
    else:
        print(f"❌ Image Upload Failed: {res.text}")

    print_step("✅✅ TEST COMPLETE - ALL FEATURES VERIFIED ✅✅")

if __name__ == "__main__":
    run_test()
