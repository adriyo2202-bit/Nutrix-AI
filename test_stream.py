import requests
import json
import sys

def main():
    print("Logging in...", flush=True)
    login_res = requests.post("http://127.0.0.1:8000/login", data={"username": "dev@cca.com", "password": "CCA_WELCOMES"})
    if not login_res.ok:
        print("Login failed", flush=True)
        return
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    query = "Make an elaborate Indian diet chart for high protein using the dataset."
    print(f"Testing /chat/stream with query: '{query}'")
    
    with requests.post("http://127.0.0.1:8000/chat/stream", json={"query": query}, headers=headers, stream=True) as r:
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received: {decoded_line}")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
