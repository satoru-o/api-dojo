import requests


def get_profile(base_url, token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(f"{base_url}/api/profile", headers=headers)
    resp.raise_for_status()
    return resp.json()
