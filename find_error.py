
import requests
import re

try:
    resp = requests.get('http://127.0.0.1:8000/list/')
    if resp.status_code == 500:
        content = resp.text
        # Look for "Reverse for"
        matches = re.findall(r"Reverse for .*? with arguments .*? and keyword arguments .*? not found", content)
        if matches:
            for m in matches:
                print(f"Found error: {m}")
        else:
            # Fallback: print exception value
            ex = re.search(r"exception_value\">(.*?)<", content)
            if ex:
                print(f"Exception Message: {ex.group(1)}")
            else:
                print("Could not parse specific error message.")
except Exception as e:
    print(e)
