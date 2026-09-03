# ヒント

- `/api/flaky` は1〜2回目は500を返し、3回目以降で200を返します（呼び出し回数はチェックの
  ケースごとにリセットされます）。`/api/flaky-always` は常に500です。
- リトライのたびに `time.sleep(...)` で少し待つのが定石です（今回は待ち時間は短くてOK）。
- 「リトライを使い切ってもダメだった」場合、`{"error": "..."}` のような辞書を返して
  握りつぶすのではなく、最後のレスポンスに対して `raise_for_status()` を呼んで
  例外をそのまま呼び出し元に伝播させてください。
- 形:
  ```python
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
  ```
