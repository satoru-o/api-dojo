# ヒント

- `/api/slow` は常に約2.5秒かかってから応答します。
- `requests.get(url, timeout=秒数)` を指定すると、その秒数以内に応答が来なければ
  `requests.exceptions.Timeout` が送出されます。`try/except` で捕まえてください。
- リトライを使い切ってもタイムアウトし続けた場合は、`except` 節で捕まえた例外を
  握りつぶさずに `raise` でそのまま外に投げ直してください。
- 形:
  ```python
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
  ```
