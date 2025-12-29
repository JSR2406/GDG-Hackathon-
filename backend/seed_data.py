
import requests
import sys

# Use local API for seeding
BASE_URL = "http://localhost:8000/api/v1"

def seed():
    print("🌱 Seeding Database for Demo Video...")
    
    # 1. Create Users
    users = [
        {"name": "Alice Logistics", "email": "alice@corp.com", "semester": 1, "department": "Logistics Bu", "hostel": "Block A"},
        {"name": "Bob IT Solutions", "email": "bob@tech.com", "semester": 1, "department": "IT Dept", "hostel": "Block B"},
        {"name": "Charlie Sales", "email": "charlie@sales.com", "semester": 1, "department": "Sales Team", "hostel": "Block C"}
    ]
    
    ids = {}
    
    for u in users:
        print(f"Creating user {u['name']}...", end=" ")
        # Try to register
        res = requests.post(f"{BASE_URL}/users/", json=u)
        if res.status_code == 200:
            uid = res.json()['id']
            print(f"✅ Created (ID: {uid})")
            ids[u['email']] = uid
        elif res.status_code == 400:
            print("⚠️ Exists, fetching...", end=" ")
            # Fallback: find user
            all_u = requests.get(f"{BASE_URL}/users/").json()
            found = next((x for x in all_u if x['email'] == u['email']), None)
            if found:
                ids[u['email']] = found['id']
                print(f"Found (ID: {found['id']})")
            else:
                print("❌ Failed to find.")
        else:
            print(f"❌ Error: {res.text}")

    # 2. Create Items (Mocking Uploads)
    # Alice has 'Server Rack'
    if 'alice@corp.com' in ids:
        uid = ids['alice@corp.com']
        # Check if already has items
        items = requests.get(f"{BASE_URL}/items/users/{uid}/items").json()
        if not items:
            item_data = {
                "name": "Enterprise Server Rack",
                "category": "Electronics",
                "condition": "Good",
                "department": "Logistics Bu",
                "photo_url": "/static/demos/server_rack.jpg" # Mock URL
            }
            requests.post(f"{BASE_URL}/items/users/{uid}/items", json=item_data)
            print("✅ Alice listed 'Enterprise Server Rack'")
        else:
            print("ℹ️ Alice already has items.")

    # Bob has 'Forklift Battery'
    if 'bob@tech.com' in ids:
        uid = ids['bob@tech.com']
        items = requests.get(f"{BASE_URL}/items/users/{uid}/items").json()
        if not items:
            item_data = {
                "name": "Industrial Forklift Battery",
                "category": "Machinery",
                "condition": "New",
                "department": "IT Dept",
                "photo_url": "/static/demos/battery.jpg"
            }
            requests.post(f"{BASE_URL}/items/users/{uid}/items", json=item_data)
            print("✅ Bob listed 'Industrial Forklift Battery'")

    print("\n✅ Seeding Complete! Ready for Demo.")

if __name__ == "__main__":
    seed()
