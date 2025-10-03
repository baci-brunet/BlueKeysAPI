# src/lib/acl.py  (no change needed if you pass a dict with "org_id")
from typing import Optional, Dict
from src.lib.db import fetch_all

def resolve_account_id_from_org(org_id: Optional[str]) -> Optional[int]:
    if not org_id:
        return None
    rows = fetch_all("SELECT id FROM accounts WHERE external_org_id = %s LIMIT 1", (org_id,))
    return rows[0]["id"] if rows else None

def restaurant_belongs_to_account(restaurant_id: int, account_id: int) -> bool:
    rows = fetch_all(
        "SELECT 1 FROM restaurants WHERE restaurantID = %s AND account_id = %s LIMIT 1",
        (restaurant_id, account_id)
    )
    return bool(rows)

def user_can_access_restaurant(auth_ctx: Dict, restaurant_id: int) -> bool:
    acct_id = resolve_account_id_from_org(auth_ctx.get("org_id"))
    return bool(acct_id) and restaurant_belongs_to_account(restaurant_id, acct_id)
