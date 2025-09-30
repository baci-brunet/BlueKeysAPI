# src/utils/response.py
import json
import os

def _cors_headers():
    # comma-separated allowed origins from env, or "*" for dev
    allowed = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    # If you’d like to echo back the request Origin when you tighten CORS later,
    # you can parse event headers instead. For now, keep it simple.
    return {
        "Access-Control-Allow-Origin": allowed,
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }

def _headers(extra=None):
    base = {"Content-Type": "application/json"}
    base.update(_cors_headers())
    if extra:
        base.update(extra)
    return base

def _resp(code, body=None, headers=None):
    return {
        "statusCode": code,
        "headers": _headers(headers),
        "body": json.dumps(body if body is not None else {})
    }

def ok(body=None): return _resp(200, body or {"ok": True})
def created(body=None): return _resp(201, body or {"ok": True})
def bad_request(msg="Bad Request"): return _resp(400, {"error": msg})
def unauthorized(msg="Unauthorized"): return _resp(401, {"error": msg})
def forbidden(msg="Forbidden"): return _resp(403, {"error": msg})
def server_error(msg="Internal Server Error"): return _resp(500, {"error": msg})