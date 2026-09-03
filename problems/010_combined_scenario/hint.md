# ヒント

- これまでの問題の組み合わせです。
  - 004: `Authorization: Bearer <token>` ヘッダー
  - 007: `total_pages` を見ながら全ページ回るループ
  - 008: 429が返ってきたら `Retry-After` の秒数だけ待ってリトライ
  - 004/006/009: 401などのエラーは握りつぶさず `raise_for_status()` で伝播させる
- ページを取得するたびに、429ハンドリングとページネーションの両方を意識する必要があります。
  「1リクエスト送って、429ならリトライ、200ならそのページのitemsを処理して次のページへ」
  という流れをループの中に書くとスッキリします。
- 形:
  ```python
  import time

  import requests


  def list_admin_users(base_url, token):
      headers = {"Authorization": f"Bearer {token}"}
      admin_names = []
      page = 1
      while True:
          resp = requests.get(
              f"{base_url}/api/secure/users",
              headers=headers,
              params={"page": page, "limit": 10},
          )
          if resp.status_code == 429:
              wait_seconds = float(resp.headers.get("Retry-After", "1"))
              time.sleep(wait_seconds)
              continue
          resp.raise_for_status()
          data = resp.json()
          admin_names.extend(item["name"] for item in data["items"] if item["role"] == "admin")
          if page >= data["total_pages"]:
              break
          page += 1
      return admin_names
  ```
