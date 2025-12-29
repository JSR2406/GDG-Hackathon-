
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    print("🧪 Testing Candidate Registration Flow...")
    
    # 1. New Candidate Data
    new_user = {
        "name": "Candidate Zero",
        "email": "candidate@zero.com",
        "semester": 1,
        "department": "HR",
        "hostel": "Office 1"
    }
    
    # 2. Register
    print(f"Registering {new_user['email']}...")
    res = requests.post(f"{BASE_URL}/users/", json=new_user)
    
    if res.status_code == 200:
        user_data = res.json()
        print(f"✅ Registration Success! ID: {user_data['id']}")
        
        # 3. Verify Persistence (Login simulation)
        print("Verifying persistence via Lookup...")
        all_users = requests.get(f"{BASE_URL}/users/").json()
        found = next((x for x in all_users if x['email'] == new_user['email']), None)
        
        if found:
            print(f"✅ Candidate verified in Database. ID: {found['id']}")
        else:
            print("❌ Error: User registered but not found in list.")
            
    elif res.status_code == 400 and "already registered" in res.text:
        print("⚠️ Candidate already exists (Test is idempotent).")
        # Verify anyway
        all_users = requests.get(f"{BASE_URL}/users/").json()
        found = next((x for x in all_users if x['email'] == new_user['email']), None)
        if found: print(f"✅ Verified existing candidate. ID: {found['id']}")
        
    else:
        print(f"❌ Registration Failed: {res.text}")

if __name__ == "__main__":
    test_registration()
