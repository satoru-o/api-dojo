"""api-dojo の疑似APIサーバー。標準ライブラリの http.server のみで実装する。

`uv run dojo.py check` の実行中、dojo.py が create_server() でこのサーバーを
127.0.0.1のランダムな空きポートに起動し、workspace/answer.py のクライアントコードから
リクエストを受ける。エンドポイント仕様は docs/api_reference.md を参照。
"""

from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

TOKEN = "dojo-secret-token"

USERS = [
    {"id": i, "name": f"user{i:02d}", "role": "admin" if i % 5 == 0 else "member"}
    for i in range(1, 26)
]

PROFILE = {"id": 1, "name": "Ada", "role": "admin"}

SLOW_DELAY_SECONDS = 2.5
DEFAULT_LIMIT = 10

_state = {
    "items": [],
    "flaky_calls": 0,
    "limited_calls": 0,
    "secure_first_call_done": False,
}


def reset_state() -> None:
    """各テストケースの直前に呼ばれ、サーバー内部のカウンタ・ストアを初期状態に戻す。"""
    _state["items"] = []
    _state["flaky_calls"] = 0
    _state["limited_calls"] = 0
    _state["secure_first_call_done"] = False


def _paginate(items: list, page: int, limit: int) -> dict:
    total = len(items)
    total_pages = max(1, -(-total // limit))
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": items[start:end],
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, status: int, payload: dict, headers: dict | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _bearer_token(self) -> str | None:
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[len("Bearer "):]
        return None

    def _route(self) -> tuple[str, dict]:
        parsed = urlparse(self.path)
        return parsed.path, {k: v[0] for k, v in parse_qs(parsed.query).items()}

    def _handle_users_page(self, query: dict) -> None:
        page = int(query.get("page", 1))
        limit = int(query.get("limit", DEFAULT_LIMIT))
        result = _paginate(USERS, page, limit)
        if page < 1 or page > result["total_pages"]:
            self._send_json(404, {"error": "not_found"})
            return
        self._send_json(200, result)

    def do_GET(self):
        path, query = self._route()

        if path == "/api/status":
            self._send_json(200, {"service": "api-dojo", "version": "1.0.0", "status": "ok"})
            return

        if path == "/api/users":
            self._handle_users_page(query)
            return

        if path == "/api/profile":
            if self._bearer_token() == TOKEN:
                self._send_json(200, PROFILE)
            else:
                self._send_json(401, {"error": "unauthorized"})
            return

        if path == "/api/status-demo":
            code = query.get("code", "200")
            responses = {
                "200": (200, {"status": "ok", "data": "hello"}),
                "400": (400, {"error": "bad_request"}),
                "401": (401, {"error": "unauthorized"}),
                "404": (404, {"error": "not_found"}),
                "500": (500, {"error": "server_error"}),
            }
            status, payload = responses.get(code, (400, {"error": "bad_request"}))
            self._send_json(status, payload)
            return

        if path == "/api/flaky":
            _state["flaky_calls"] += 1
            n = _state["flaky_calls"]
            if n <= 2:
                self._send_json(500, {"error": "server_error"})
            else:
                self._send_json(200, {"status": "ok", "attempt": n})
            return

        if path == "/api/flaky-always":
            self._send_json(500, {"error": "server_error"})
            return

        if path == "/api/limited":
            _state["limited_calls"] += 1
            n = _state["limited_calls"]
            if n <= 2:
                self._send_json(429, {"error": "rate_limited"}, headers={"Retry-After": "1"})
            else:
                self._send_json(200, {"status": "ok"})
            return

        if path == "/api/slow":
            time.sleep(SLOW_DELAY_SECONDS)
            self._send_json(200, {"status": "ok", "slept": True})
            return

        if path == "/api/secure/users":
            if self._bearer_token() != TOKEN:
                self._send_json(401, {"error": "unauthorized"})
                return
            if not _state["secure_first_call_done"]:
                _state["secure_first_call_done"] = True
                self._send_json(429, {"error": "rate_limited"}, headers={"Retry-After": "1"})
                return
            self._handle_users_page(query)
            return

        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        path, _ = self._route()

        if path == "/api/items":
            data = self._read_json()
            name = data.get("name")
            if not name:
                self._send_json(400, {"error": "bad_request"})
                return
            item = {"id": len(_state["items"]) + 1, "name": name}
            _state["items"].append(item)
            self._send_json(201, item)
            return

        self._send_json(404, {"error": "not_found"})


def create_server() -> ThreadingHTTPServer:
    """/api/slow のような時間のかかるエンドポイントが他のリクエストをブロックしないよう、
    リクエストごとにスレッドを立てる ThreadingHTTPServer を使う。"""
    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
