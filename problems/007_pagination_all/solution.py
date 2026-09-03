import requests


def get_all_users(base_url):
    names = []
    page = 1
    while True:
        resp = requests.get(f"{base_url}/api/users", params={"page": page, "limit": 10})
        data = resp.json()
        names.extend(item["name"] for item in data["items"])
        if page >= data["total_pages"]:
            break
        page += 1
    return names
