import json
from src.utils.response import ok, bad_request, forbidden
from src.lib.auth import get_auth_context
from src.lib.acl import user_can_access_restaurant
from src.lib.db import fetch_all

def get(event, context):
    """
    Returns recent check data for a single restaurant.
    Expects JSON body: { "restaurant_id": <int> }
    (Falls back to querystring ?restaurant_id=<int> if body is absent.)
    """
    auth = get_auth_context(event)

    # 1) Parse restaurant_id from JSON body
    rid = None
    body = event.get("body")
    if body:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return bad_request("Invalid JSON body")
        rid = payload.get("restaurant_id")

    # 2) Fallback: querystring (useful for quick testing)
    if rid is None:
        qs = event.get("queryStringParameters") or {}
        rid = qs.get("restaurant_id")

    if rid is None:
        return bad_request("restaurant_id is required")

    # 3) Validate type (must be int)
    try:
        restaurant_id = int(rid)
    except (TypeError, ValueError):
        return bad_request("restaurant_id must be an integer")

    # 4) Authorization: ensure this restaurant belongs to caller's account
    if not user_can_access_restaurant(auth, restaurant_id):
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