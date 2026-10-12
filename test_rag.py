import requests

print("Logging in...")
login_response = requests.post("http://127.0.0.1:8000/login", data={"username": "dev@cca.com", "password": "CCA_WELCOMES"})

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Testing RAG via /chat endpoint...")
chat_response = requests.post("http://127.0.0.1:8000/chat", json={"query": "What is protein?"}, headers=headers)

if chat_response.status_code == 200:
    print("RAG query successful!")
    print(chat_response.json())
else:
    print(f"RAG query failed: {chat_response.status_code} {chat_response.text}")
