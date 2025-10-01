import json
from src.utils.response import ok, bad_request, forbidden
from src.lib.auth import get_org_id
from src.lib.acl import user_can_access_restaurant
from src.lib.db import fetch_all

def get(event, context):
        # Parse JSON body
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return bad_request("content is not proper json!")

    restaurant_id = body.get("restaurant_id")
    if not isinstance(restaurant_id, int):
        return bad_request("restaurant_id (int) is required")

    # Enforce active org in token (your rule)
    org_id = get_org_id(event)
    if not org_id:
        return forbidden("No active organization in token")

    # Enforce tenant boundary
    if not user_can_access_restaurant({"org_id": org_id}, restaurant_id):
        return forbidden("No access to this restaurant")

    # 5) Fetch & return data (tweak LIMIT as needed)
    rows = fetch_all(
        """
        SELECT id, diner_id, check_total, check_date
        FROM checks
        WHERE restaurant_id = %s
        ORDER BY check_date DESC
        LIMIT 50
        """,
        (restaurant_id,),
    )

    return ok({"restaurant_id": restaurant_id, "data": rows})