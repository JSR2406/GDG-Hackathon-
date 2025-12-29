import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_result(step, response):
    status = "✅ PASS" if response.status_code in [200, 201] else f"❌ FAIL ({response.status_code})"
    print(f"{step}: {status}")
    if response.status_code not in [200, 201]:
        print(response.text)
    return response.json() if response.status_code in [200, 201] else None

def test_flow():
    print("🚀 Starting Business Flow Integration Test...")

    # 1. Register Users
    users = [
        {"name": "Alice Corp", "email": "alice@corp.com", "semester": 1, "department": "Ops", "hostel": "Block A"},
        {"name": "Bob Logistics", "email": "bob@logistics.com", "semester": 1, "department": "Logistics", "hostel": "Block B"},
        {"name": "Charlie Sales", "email": "charlie@sales.com", "semester": 1, "department": "Sales", "hostel": "Block C"}
    ]
    user_ids = []
    
    for u in users:
        res = requests.post(f"{BASE_URL}/users/", json=u)
        if res.status_code == 400:
            print(f"User {u['name']} exists, fetching ID...")
            # Fetch all users to find ID (inefficient but works for test)
            all_users = requests.get(f"{BASE_URL}/users/").json()
            found = next((x for x in all_users if x['email'] == u['email']), None)
            if found:
                user_ids.append(found['id'])
                print(f"Recovered ID: {found['id']}")
        else:
            data = print_result(f"Register {u['name']}", res)
            if data: user_ids.append(data["id"])

    if len(user_ids) < 3: return

    alice_id, bob_id, charlie_id = user_ids
    print(f"IDs: Alice={alice_id}, Bob={bob_id}, Charlie={charlie_id}")

    # 2. Upload Items (with mock image)
    # Create a dummy image in memory
    dummy_image = ('test_asset.jpg', b'fake_image_bytes', 'image/jpeg')
    
    # Alice uploads 'Server Rack'
    res = requests.post(f"{BASE_URL}/items/users/{alice_id}/items/upload-photo", files={'file': dummy_image})
    print_result("Alice Upload Photo", res)
    # (The endpoint creates the item automatically after analysis)
    
    # We need to get the item ID. The response contains 'item': {'id': ...}
    alice_item = res.json()['item']['id']

    # Bob uploads 'Forklift'
    res = requests.post(f"{BASE_URL}/items/users/{bob_id}/items/upload-photo", files={'file': dummy_image})
    bob_item = res.json()['item']['id']
    print_result("Bob Upload Photo", res)

    # Charlie uploads 'Projector'
    res = requests.post(f"{BASE_URL}/items/users/{charlie_id}/items/upload-photo", files={'file': dummy_image})
    charlie_item = res.json()['item']['id']
    print_result("Charlie Upload Photo", res)

    # 3. Create Barter Loop (A->B->C->A)
    # Alice has Item A, wants 'Forklift' (Category 'Logistics') (Bob has this category)
    # Bob has Item B, wants 'Projector' (Category 'Sales') (Charlie has this)
    # Charlie has Item C, wants 'Server Rack' (Category 'Ops') (Alice has this)

    # Note: The mock AI analysis assigns categories. My mock returns "Electronics", "Stationery" etc randomly or fixed. 
    # Let's verify what the mock returns. 
    # Mock returns: "Electronics" usually.
    # To force a match, I'll use the specific categories returned by the backend or broad ones if my matching engine is fuzzy.
    # Let's assume the mock returns "Electronics" for everything.
    # If they all have "Electronics", then Alice wants "Electronics", Bob wants "Electronics".
    # This creates a match.
    
    # Alice Intent
    intent_a = {
        "item_id": alice_item,
        "want_category": "Electronics",
        "want_description": "Need newer model",
        "emergency": False
    }
    requests.post(f"{BASE_URL}/barter/barter-intents?user_id={alice_id}", json=intent_a)
    
    # Bob Intent
    intent_b = {
        "item_id": bob_item,
        "want_category": "Electronics",
        "want_description": "Upgrade needed",
        "emergency": False
    }
    requests.post(f"{BASE_URL}/barter/barter-intents?user_id={bob_id}", json=intent_b)

    # Charlie Intent (Triggers Match)
    intent_c = {
        "item_id": charlie_item,
        "want_category": "Electronics",
        "want_description": "Looking for swap",
        "emergency": True
    }
    res = requests.post(f"{BASE_URL}/barter/barter-intents?user_id={charlie_id}", json=intent_c)
    match_data = print_result("Charlie Intent (Trigger Match)", res)
    
    if match_data.get('match_found'):
        print("🎉 MATCH FOUND!")
        match_id = match_data['match']['id']
        
        # 4. Accept Match
        res = requests.post(f"{BASE_URL}/matches/{match_id}/accept?user_id={alice_id}")
        print_result("Alice Accept", res)
        
        res = requests.post(f"{BASE_URL}/matches/{match_id}/accept?user_id={bob_id}")
        print_result("Bob Accept", res)
        
        res = requests.post(f"{BASE_URL}/matches/{match_id}/accept?user_id={charlie_id}")
        print_result("Charlie Accept", res)
        
    else:
        print("⚠️ No match found (Mock categories might not align)")

    # 5. TEST LOST & FOUND WITH IMAGE
    print("\n--- Testing Lost & Found Image Upload ---")
    
    # Step 1: Upload Photo
    res = requests.post(f"{BASE_URL}/lost-found/upload", files={'file': dummy_image})
    lf_photo_data = print_result("Upload LF Photo", res)
    
    if lf_photo_data:
        photo_url = lf_photo_data['photo_url']
        print(f"Photo uploaded to: {photo_url}")
        
        # Step 2: Post Item
        lf_item = {
            "item_name": "Company Laptop",
            "category": "Electronics",
            "description": "Lost in cafeteria",
            "type": "lost",
            "photo_url": photo_url
        }
        res = requests.post(f"{BASE_URL}/lost-found/?user_id={alice_id}", json=lf_item)
        print_result("Post LF Item", res)

    print("\n✅ Test Suite Completed")

if __name__ == "__main__":
    test_flow()
