import requests
import sys

def test_analytics():
    # 1. Login
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {"email": "admin@servicedesk.com", "password": "admin"}
    
    print("Logging in...")
    resp = requests.post(login_url, json=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Analytics
    analytics_url = "http://localhost:8000/api/analytics/"
    print(f"Fetching analytics from {analytics_url}...")
    resp = requests.get(analytics_url, headers=headers)
    
    if resp.status_code == 200:
        print("✅ Analytics Fetched Successfully:")
        import json
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    test_analytics()
