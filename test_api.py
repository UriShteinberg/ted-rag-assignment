import requests

url = "http://127.0.0.1:3000/api/prompt"
payload = {"question": "Who spoke about education?"}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)