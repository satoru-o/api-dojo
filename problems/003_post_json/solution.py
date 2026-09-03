import requests


def create_items(base_url, names):
    results = []
    for name in names:
        resp = requests.post(f"{base_url}/api/items", json={"name": name})
        results.append(resp.json())
    return results
