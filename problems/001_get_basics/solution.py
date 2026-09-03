import requests


def get_service_status(base_url):
    resp = requests.get(f"{base_url}/api/status")
    data = resp.json()
    return data["status"]
