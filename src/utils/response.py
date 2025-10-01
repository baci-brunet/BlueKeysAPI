# src/utils/response.py
import json
from typing import Any, Dict, Optional, Callable
import traceback

JSON_HEADERS: Dict[str, str] = {"Content-Type": "application/json"}

def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    return {**JSON_HEADERS, **(extra or {})}

def _resp(status: int, body: Any = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return {
        "statusCode": status,
        "headers": _headers(headers),
        "body": json.dumps({} if body is None else body),
    }

# Success
def ok(body: Any = None): return _resp(200, body or {"ok": True})
def created(body: Any = None): return _resp(201, body or {"ok": True})

# Errors (consistent JSON shapes)
def bad_request(msg: str = "Bad Request"): return _resp(400, {"error": msg})
def unauthorized(msg: str = "Unauthorized"): return _resp(401, {"error": msg})
def forbidden(msg: str = "Forbidden"): return _resp(403, {"error": msg})
def not_found(msg: str = "Not Found"): return _resp(404, {"error": msg})
def conflict(msg: str = "Conflict"): return _resp(409, {"error": msg})
def server_error(msg: str = "Internal Server Error"): return _resp(500, {"error": msg})
