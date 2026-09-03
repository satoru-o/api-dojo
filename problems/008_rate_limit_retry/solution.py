import time

import requests


def fetch_rate_limited(base_url):
    while True:
        resp = requests.get(f"{base_url}/api/limited")
        if resp.status_code == 429:
            wait_seconds = float(resp.headers.get("Retry-After", "1"))
            time.sleep(wait_seconds)
            continue
        return resp.json()
