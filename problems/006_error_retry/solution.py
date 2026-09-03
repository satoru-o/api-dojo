import time

import requests


def fetch_with_retry(base_url, path, max_retries=5):
    last_resp = None
    for _ in range(max_retries):
        resp = requests.get(f"{base_url}{path}")
        if resp.status_code == 200:
            return resp.json()
        last_resp = resp
        time.sleep(0.1)
    last_resp.raise_for_status()
