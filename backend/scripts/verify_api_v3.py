import requests
import sys

# Using internal container URL if running from within the container network, 
# but here we hit it from outside or via localhost if mapped.
# If running inside the container, we should use http://localhost:8000 (backend port) 
# OR use the service name 'backend:8000'.
# BUT, the script is running 'docker compose exec backend python ...', 
# which means it runs INSIDE the container. 
# Inside the container, the backend is likely listening on 0.0.0.0:8000.

BASE_URL = "http://localhost:8000/api"

def get_token():
    login_data = {"email": "admin@servicedesk.com", "password": "admin"}
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def verify_analytics(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/analytics", headers=headers)
    if response.status_code == 200:
        print("✅ Analytics API is working")
        data = response.json()
        print(f"   Trends: {len(data['volume_trends'])} days")
        print(f"   Agents: {len(data['agent_performance'])} agents")
    else:
        print(f"❌ Analytics API failed: {response.status_code} - {response.text}")

def verify_crm(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/?role=CLIENT", headers=headers)
    if response.status_code == 200:
        print("✅ CRM (Users) API is working")
        data = response.json()
        print(f"   Clients count: {len(data)}")
    else:
        print(f"❌ CRM API failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        verify_analytics(token)
        verify_crm(token)
    else:
        sys.exit(1)
