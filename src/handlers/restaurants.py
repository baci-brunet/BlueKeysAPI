import json
from pymysql import err as mysql_err
from src.utils.response import ok, bad_request, forbidden, server_error, conflict
from src.lib.auth import get_user_id, get_org_id, get_role
from src.lib.acl import resolve_account_id_from_org
from src.lib.db import fetch_all, execute

ALLOWED_CREATOR_ROLES = {"org:admin", "org:manager"}

def post(event, context):
    # 1) Identity & tenant from verified JWT claims (set by HTTP API JWT authorizer)
    clerk_user_id = get_user_id(event)   # JWT 'sub'
    org_id = get_org_id(event)           # your custom 'org_id' claim
    role = get_role(event)

    if not clerk_user_id:
        return forbidden("Missing subject in token")
    if not org_id:
        return forbidden("No active organization in token")
    if role not in ALLOWED_CREATOR_ROLES:
        return forbidden("Insufficient role to create restaurants")

    # 2) Map org_id -> account_id to enforce tenant boundary
    account_id = resolve_account_id_from_org(org_id)
    if account_id is None:
        return forbidden("Unknown organization")

    # Parse & validate body
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return bad_request("Invalid JSON body")

    name = body.get("name")
    address = body.get("address")

    if not isinstance(name, str) or not name.strip():
        return bad_request("Field 'name' (non-empty string) is required")
    name = name.strip()

    if not isinstance(address, str) or not address.strip():
        address = ""

    # Insert (adjust columns as per your schema; created_by_user_id optional)
    try:
        res = execute(
            """
            INSERT INTO restaurants (account_id, name, address)
            VALUES (%s, %s, %s)
            """,
            (account_id, name, address,),
        )
    except mysql_err.IntegrityError as e:
        # e.g., UNIQUE(account_id, name) violation
        return conflict("Restaurant already exists for this organization")
    except Exception:
        return server_error()

    new_id = res.get("lastrowid")
    return ok({"restaurant": {"id": new_id, "name": name}})

def get(event, context):
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
        SELECT restaurantID, account_id, name
        FROM restaurants
        WHERE account_id = %s
        ORDER BY name ASC
        """,
        (account_id,),
    )

    if not rows:
        return bad_request("Restaurants not found")

    return ok({"restaurants": rows[0]})