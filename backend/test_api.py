import requests

try:
    response = requests.get('http://127.0.0.1:8000/api/videos')
    response.raise_for_status()
    print("Success")
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Other Error: {e}")
