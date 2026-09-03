import requests


def fetch_with_timeout_retry(base_url, timeout_seconds, max_retries):
    last_error = None
    for _ in range(max_retries):
        try:
            resp = requests.get(f"{base_url}/api/slow", timeout=timeout_seconds)
            return resp.json()
        except requests.exceptions.Timeout as e:
            last_error = e
    raise last_error
