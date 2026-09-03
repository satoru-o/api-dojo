# ヒント

- `requests.get(url, params={...})` の `params` にdictを渡すと、`?page=1&limit=10` のような
  クエリ文字列を自動的に組み立ててくれます。
- レスポンスのJSONは `{"page":..., "limit":..., "total":..., "total_pages":..., "items":[...]}`
  という形です。`items` の各要素が `{"id":..., "name":..., "role":...}` です。
- 形:
  ```python
  import requests


  def get_user_names(base_url, page, limit):
      resp = requests.get(f"{base_url}/api/users", params={"page": page, "limit": limit})
      data = resp.json()
      return [item["name"] for item in data["items"]]
  ```
