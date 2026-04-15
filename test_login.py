import requests
import sys

def test_login(email, password):
    url = "http://localhost/api/auth/login"
    try:
        response = requests.post(url, json={"email": email, "password": password})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "agent1@servicedesk.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin"
    test_login(email, password)
