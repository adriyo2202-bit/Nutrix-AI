import requests
import json
import sys

print("Logging in...")
login_response = requests.post("http://127.0.0.1:8000/login", data={"username": "dev@cca.com", "password": "CCA_WELCOMES"})

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    sys.exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

query = "Make an elaborate Indian diet chart for high protein using the dataset."
print(f"Testing RAG via /chat endpoint with query: '{query}'")
chat_response = requests.post("http://127.0.0.1:8000/chat", json={"query": query}, headers=headers)

if chat_response.status_code == 200:
    print("RAG query successful!\n")
    # Encode to bytes and print to avoid cp1252 crash in Windows console
    answer = chat_response.json().get('answer', '')
    sys.stdout.buffer.write(answer.encode('utf-8'))
    print("\n")
else:
    print(f"RAG query failed: {chat_response.status_code} {chat_response.text}")
