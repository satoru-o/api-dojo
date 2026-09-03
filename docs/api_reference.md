# 疑似API仕様書

api-dojo が同梱する疑似APIサーバー（`server/pseudo_api.py`）の仕様です。
実務でAPIクライアントを書くときにまず読む「公式ドキュメント」に相当するものなので、
問題を解く前にひととおり目を通してください。

`uv run dojo.py check` を実行すると、このサーバーが `127.0.0.1` の空いているポートで
自動的に起動し、`workspace/answer.py` からのリクエストを受けたあと自動的に停止します。
**手動でサーバーを起動する必要はありません。** ベースURL（例: `http://127.0.0.1:54321`）は、
採点対象の関数の第一引数 `base_url` として渡されます。

## 認証

一部のエンドポイントは `Authorization: Bearer <token>` ヘッダーが必要です。

- 正しいトークン: `dojo-secret-token`
- ヘッダーがない、またはトークンが間違っている場合は `401 Unauthorized` を返します。

## エラーレスポンスの共通形式

エラー時は基本的に `{"error": "<種類>"}` という形のJSONを返します（例外: 429は後述）。

## エンドポイント一覧

### `GET /api/status`

サービスの状態を返します。認証不要。

```
200 OK
{"service": "api-dojo", "version": "1.0.0", "status": "ok"}
```

### `GET /api/users?page=<int>&limit=<int>`

ユーザー一覧をページ単位で返します（全25件）。`page` の既定値は1、`limit` の既定値は10。
認証不要。

```
200 OK
{
  "page": 1,
  "limit": 10,
  "total": 25,
  "total_pages": 3,
  "items": [
    {"id": 1, "name": "user01", "role": "member"},
    ...
  ]
}
```

`role` は `id % 5 == 0` のユーザーだけ `"admin"`、それ以外は `"member"` です。
存在しないページ番号（1未満、または `total_pages` 超過）を指定すると `404 Not Found` を返します。

### `POST /api/items`

JSONボディ `{"name": "<文字列>"}` を受け取り、新しいアイテムを作成します。認証不要。

```
201 Created
{"id": 1, "name": "Widget"}
```

`id` はサーバー起動（＝チェックの各ケース開始）のたびに1から採番し直されます。
`name` が空/欠けている場合は `400 Bad Request` を返します。

### `GET /api/profile`

`Authorization: Bearer dojo-secret-token` が必要です。

```
200 OK
{"id": 1, "name": "Ada", "role": "admin"}
```

トークンがない/間違っている場合:

```
401 Unauthorized
{"error": "unauthorized"}
```

### `GET /api/status-demo?code=<200|400|401|404|500>`

指定したステータスコードに応じたレスポンスをそのまま返す、ステータス分岐の練習用エンドポイントです。
認証不要。

| `code` | 実際のHTTPステータス | ボディ |
|---|---|---|
| `200` | 200 | `{"status": "ok", "data": "hello"}` |
| `400` | 400 | `{"error": "bad_request"}` |
| `401` | 401 | `{"error": "unauthorized"}` |
| `404` | 404 | `{"error": "not_found"}` |
| `500` | 500 | `{"error": "server_error"}` |

### `GET /api/flaky`

不安定なエンドポイントです。**チェックの各ケース開始時にリセットされる**呼び出し回数を内部で数えており、

- 1〜2回目の呼び出し: `500 Internal Server Error`、`{"error": "server_error"}`
- 3回目以降の呼び出し: `200 OK`、`{"status": "ok", "attempt": <その時点の呼び出し回数>}`

### `GET /api/flaky-always`

常に `500 Internal Server Error`、`{"error": "server_error"}` を返します。
リトライを使い切って諦めるケースの練習用です。

### `GET /api/limited`

レート制限のあるエンドポイントです（呼び出し回数はケース開始時にリセット）。

- 1〜2回目の呼び出し: `429 Too Many Requests`、レスポンスヘッダー `Retry-After: 1`、
  ボディ `{"error": "rate_limited"}`
- 3回目以降の呼び出し: `200 OK`、`{"status": "ok"}`

`Retry-After` ヘッダーの値は待つべき秒数です。

### `GET /api/slow`

常に約2.5秒スリープしてから `200 OK`、`{"status": "ok", "slept": true}` を返します。
タイムアウトの練習用です。

### `GET /api/secure/users?page=<int>&limit=<int>`

`/api/users` の認証付き・レート制限付きバージョンです。

- `Authorization: Bearer dojo-secret-token` がない/間違っている場合: `401 Unauthorized`、
  `{"error": "unauthorized"}`
- 認証OKでも、**ケース開始後の最初の1回だけ** `429 Too Many Requests`
  （`Retry-After: 1`、`{"error": "rate_limited"}`）を返します。2回目以降は通常どおり
  `/api/users` と同じ形式のページネーションレスポンスを返します。

## 参考: `requests` での典型パターン

```python
import requests

# 基本のGET
resp = requests.get(f"{base_url}/api/status")
resp.json()["status"]

# クエリパラメータ
resp = requests.get(f"{base_url}/api/users", params={"page": 1, "limit": 10})

# JSONボディ付きPOST
resp = requests.post(f"{base_url}/api/items", json={"name": "Widget"})

# 認証ヘッダー
resp = requests.get(f"{base_url}/api/profile", headers={"Authorization": f"Bearer {token}"})

# ステータスコードで例外を送出させる
resp.raise_for_status()  # 4xx/5xxなら requests.exceptions.HTTPError を送出

# タイムアウト
try:
    resp = requests.get(f"{base_url}/api/slow", timeout=1)
except requests.exceptions.Timeout:
    ...
```
