import requests

def test():
    # Login
    resp = requests.post('http://127.0.0.1:8000/login', data={'username':'dev@cca.com', 'password':'CCA_WELCOMES'})
    if not resp.ok:
        print("Login failed", resp.text)
        return
    token = resp.json()['access_token']
    
    # Upload
    with open('test1.png', 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.post('http://127.0.0.1:8000/analyze-label', headers=headers, files=files, timeout=600)
        
    print(resp.status_code)
    try:
        print(resp.json())
    except:
        print(resp.text)

if __name__ == '__main__':
    test()
