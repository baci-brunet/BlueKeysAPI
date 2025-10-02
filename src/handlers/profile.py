import json
from src.utils.response import ok, bad_request, forbidden
from src.lib.auth import get_user_id, get_org_id
from src.lib.acl import resolve_account_id_from_org
from src.lib.db import fetch_all

def post(event, context):
    # 1) Identity & tenant from verified JWT claims (set by HTTP API JWT authorizer)
    clerk_user_id = get_user_id(event)   # JWT 'sub'
    org_id = get_org_id(event)           # your custom 'org_id' claim

    if not clerk_user_id:
        return forbidden("Missing subject in token")
    if not org_id:
        return forbidden("No active organization in token")

    # 2) Map org_id -> account_id to enforce tenant boundary
    account_id = resolve_account_id_from_org(org_id)
    if account_id is None:
        return forbidden("Unknown organization")

    # 3) Fetch user *within* the caller's tenant (account)
    rows = fetch_all(
        """
        SELECT id, email, clerk_user_id, created_at
        FROM users
        WHERE clerk_user_id = %s
        LIMIT 1
        """,
        (clerk_user_id, account_id),
    )

    if not rows:
        return bad_request("User not found")

    return ok({"user": rows[0]})