# ヒント

- `requests.post(url, json={...})` の `json` にdictを渡すと、自動的にJSONへ変換して
  `Content-Type: application/json` ヘッダーも付けて送ってくれます。
- 作成に成功すると `201 Created` と `{"id": N, "name": "..."}` が返ってきます。
- 形:
  ```python
  import requests


  def create_items(base_url, names):
      results = []
      for name in names:
          resp = requests.post(f"{base_url}/api/items", json={"name": name})
          results.append(resp.json())
      return results
  ```
