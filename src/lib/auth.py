from typing import Any, Dict

def get_auth_context(event: Dict[str, Any]) -> Dict[str, Any]:
    return event.get("requestContext", {}).get("authorizer", {}) or {}

def has_scope(context: Dict[str, Any], required: str) -> bool:
    scope = context.get("scope", "")
    return required in set(scope.split()) if isinstance(scope, str) else False