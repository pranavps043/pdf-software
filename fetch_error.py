
import requests
try:
    resp = requests.get('http://127.0.0.1:8000/list/')
    print(f"Status: {resp.status_code}")
    if resp.status_code == 500:
        # Print the first 2000 chars and search for exception class
        print(resp.text[:4000]) 
except Exception as e:
    print(e)
