import json
from src.utils.response import ok, bad_request, forbidden
from src.lib.auth import get_auth_context
from src.lib.acl import user_can_access_restaurant
from src.lib.db import fetch_all

def post(event, context):
    uid = None
    body = event.get("body")
    if body:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return bad_request("Invalid JSON body")
        uid = payload.get("clerk_user_id")

    # 2) Fallback: querystring (useful for quick testing)
    if uid is None:
        qs = event.get("queryStringParameters") or {}
        uid = qs.get("clerk_user_id")

    if uid is None:
        return bad_request("clerk_user_id is required")

    # 3) Validate type (must be int)
    try:
        clerk_id = str(id)
    except (TypeError, ValueError):
        return bad_request("clerk_user_id must be a string")

    # 5) Fetch & return data (tweak LIMIT as needed)
    rows = fetch_all(
        """
        SELECT user_id, email, created_at
        FROM users
        WHERE clerk_user_id = %s
        LIMIT 10
        """,
        (clerk_id,),
    )

    return ok({"clerk_user_id": clerk_id, "data": rows})