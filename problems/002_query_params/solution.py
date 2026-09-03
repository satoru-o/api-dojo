import requests


def get_user_names(base_url, page, limit):
    resp = requests.get(f"{base_url}/api/users", params={"page": page, "limit": limit})
    data = resp.json()
    return [item["name"] for item in data["items"]]
