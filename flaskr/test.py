import requests

print(requests.get("http://0.0.0.0:8000/api/get_info").json())