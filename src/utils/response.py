# src/utils/response.py (or http.py)
import json, os, traceback
from functools import wraps
from typing import Any, Dict, Optional, Callable

def _cors_headers() -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": os.getenv("CORS_ALLOWED_ORIGINS", "*"),
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }

def _resp(status: int, body: Any = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    base = {"Content-Type": "application/json", **_cors_headers(), **(headers or {})}
    return {"statusCode": status, "headers": base, "body": json.dumps(body if body is not None else {})}

def ok(body=None):             return _resp(200, body or {"ok": True})
def created(body=None):        return _resp(201, body or {"ok": True})
def bad_request(msg="Bad Request"):  return _resp(400, {"error": msg})
def server_error(msg="Internal Server Error"): return _resp(500, {"error": msg})

def _is_options(event: Dict[str, Any]) -> bool:
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    return (method or "").upper() == "OPTIONS"

def _ensure_cors(resp: Dict[str, Any]) -> Dict[str, Any]:
    # Merge CORS headers into any Lambda-proxy style response
    headers = resp.get("headers") or {}
    headers = {**_cors_headers(), **headers}
    resp["headers"] = headers
    return resp

def with_cors(handler: Callable[[Dict[str, Any], Any], Dict[str, Any]]):
    """
    Decorator that:
      • returns 204 for OPTIONS with CORS headers
      • wraps unhandled exceptions as 500 JSON with CORS
      • ensures CORS headers exist on any normal return
    """
    @wraps(handler)
    def _wrapped(event, context):
        if _is_options(event):
            return {"statusCode": 204, "headers": _cors_headers(), "body": ""}
        try:
            resp = handler(event, context)
            return _ensure_cors(resp)
        except Exception as e:
            # Log full traceback for CloudWatch debugging
            print("[UNHANDLED ERROR]", e)
            print(traceback.format_exc())
            return server_error()
    return _wrapped
