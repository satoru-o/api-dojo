# ヒント

- `requests.get(url)` でGETリクエストを送れます。
- レスポンスの `.json()` メソッドでJSONをPythonの辞書に変換できます。
- 形:
  ```python
  import requests


  def get_service_status(base_url):
      resp = requests.get(f"{base_url}/api/status")
      data = resp.json()
      return data["status"]
  ```
- `base_url` は `uv run dojo.py check` が疑似APIサーバーを起動したときに自動で渡してくれます。
  自分でサーバーを起動する必要はありません。
