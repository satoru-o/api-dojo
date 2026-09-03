# ヒント

- 認証トークンは `headers={"Authorization": f"Bearer {token}"}` のように
  `requests.get` の `headers` 引数へdictで渡します。
- `token` が `None` のときはヘッダーを付けない（空のdictを渡す）でOKです。
- 4xx/5xxが返ってきたときに `resp.raise_for_status()` を呼ぶと、
  `requests.exceptions.HTTPError` が自動的に送出されます。ここでは「握りつぶして
  別の値を返す」のではなく、この例外をそのまま呼び出し元に伝播させるのが正解です。
- 形:
  ```python
  import requests


  def get_profile(base_url, token):
      headers = {"Authorization": f"Bearer {token}"} if token else {}
      resp = requests.get(f"{base_url}/api/profile", headers=headers)
      resp.raise_for_status()
      return resp.json()
  ```
