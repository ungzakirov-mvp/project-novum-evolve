import requests
import sys
import json

# Constants - Internal Docker Network URL
BASE_URL = "http://localhost:8000/api"
EMAIL = "admin@servicedesk.com"
PASSWORD = "admin"

def verify():
    # 1. Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("Login success.")
    except Exception as e:
        print(f"Connection error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Ticket (if none)
    # We seeded statuses, so this should work.
    # Note: Tenant ID is inferred from User.
    requests.post(f"{BASE_URL}/tickets/", json={"title": "Verification Ticket", "description": "JSON check"}, headers=headers)

    # 3. Get Tickets
    print("Fetching tickets...")
    resp = requests.get(f"{BASE_URL}/tickets/", headers=headers)
    if resp.status_code == 200:
        tickets = resp.json()
        if tickets:
            print("First ticket structure:")
            print(json.dumps(tickets[0], indent=2, ensure_ascii=False))
        else:
            print("No tickets found.")
    else:
        print(f"Error fetching tickets: {resp.text}")

if __name__ == "__main__":
    verify()
