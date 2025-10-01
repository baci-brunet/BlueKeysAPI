# src/lib/auth.py
from typing import Any, Dict, Optional

def claims_from_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    HTTP API (v2) + built-in JWT authorizer puts claims here:
      event.requestContext.authorizer.jwt.claims
    """
    return (
        event.get("requestContext", {})
             .get("authorizer", {})
             .get("jwt", {})
             .get("claims", {})
        or {}
    )

def get_user_id(event: Dict[str, Any]) -> Optional[str]:
    return claims_from_event(event).get("sub")

def get_org_id(event: Dict[str, Any]) -> Optional[str]:
    return claims_from_event(event).get("org_id")

def get_role(event: Dict[str, Any]) -> Optional[str]:
    return claims_from_event(event).get("role")