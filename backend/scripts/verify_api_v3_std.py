import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000/api"

def get_token():
    login_data = json.dumps({"email": "admin@servicedesk.com", "password": "admin"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=login_data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as f:
            res = json.loads(f.read().decode('utf-8'))
            return res["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def verify_endpoint(name, path, token):
    req = urllib.request.Request(f"{BASE_URL}{path}", headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as f:
            data = json.loads(f.read().decode('utf-8'))
            print(f"✅ {name} API is working")
            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'List of ' + str(len(data)) + ' items'}")
    except Exception as e:
        print(f"❌ {name} API failed: {e}")

if __name__ == "__main__":
    token = get_token()
    if token:
        verify_endpoint("Analytics", "/analytics", token)
        verify_endpoint("CRM", "/users/?role=client", token)
    else:
        sys.exit(1)
