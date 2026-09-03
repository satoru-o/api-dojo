import requests


def check_status(base_url, code):
    resp = requests.get(f"{base_url}/api/status-demo", params={"code": code})
    mapping = {
        200: "ok",
        400: "bad_request",
        401: "unauthorized",
        404: "not_found",
        500: "server_error",
    }
    return mapping[resp.status_code]
