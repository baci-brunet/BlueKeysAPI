import json

def json_resp(code: int, body) -> dict:
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def ok(body=None): return json_resp(200, body or {"ok": True})
def created(body=None): return json_resp(201, body or {"ok": True})
def bad_request(msg="Bad Request"): return json_resp(400, {"error": msg})
def unauthorized(msg="Unauthorized"): return json_resp(401, {"error": msg})
def forbidden(msg="Forbidden"): return json_resp(403, {"error": msg})
def server_error(msg="Internal Server Error"): return json_resp(500, {"error": msg})
