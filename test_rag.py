import requests

BASE_URL = "http://127.0.0.1:8000"

def test_rag(username, password, question):
    print(f"\n--- Testing as {username} ---")
    
    # 1. Login
    print("1. Logging in to get JWT token...")
    resp = requests.post(f"{BASE_URL}/token", json={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    role = resp.json()["role"]
    print(f"Success! Role assigned: {role}")
    
    # 2. Query
    print(f"2. Asking question: '{question}'")
    query_resp = requests.post(f"{BASE_URL}/query", json={"question": question}, params={"token": token})
    
    print("\n[AI RESPONSE]")
    result = query_resp.json()
    print(result.get("answer", query_resp.text))
    print("\n[SOURCES ACCESSED]")
    print(result.get("sources_accessed"))

if __name__ == "__main__":
    question = "What is the CEO's salary and bonus structure?"
    
    # Test 1: The Engineer (Should be blocked)
    test_rag("bob_eng", "password123", question)
    
    # Test 2: The HR Manager (Should succeed)
    test_rag("alice_hr", "password123", question)
