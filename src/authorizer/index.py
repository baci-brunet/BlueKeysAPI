import os
import jwt
from jwt import PyJWKClient

CLERK_JWKS_URL = os.environ["CLERK_JWKS_URL"]
ISSUER = os.environ["CLERK_ISSUER"]
AUDIENCE = os.environ["JWT_AUDIENCE"]

_jwk_client = None
def jwk_client():
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(CLERK_JWKS_URL)
    return _jwk_client

def _policy(principal_id, effect, resource, context=None):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}],
        },
        "context": context or {},
    }

def lambda_handler(event, _ctx):
    authz = (event.get("authorizationToken") or "").strip()
    if not authz.lower().startswith("bearer "):
        raise Exception("Unauthorized")
    token = authz.split(" ", 1)[1].strip()

    signing_key = jwk_client().get_signing_key_from_jwt(token).key
    claims = jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=AUDIENCE,
        issuer=ISSUER,
        options={"require": ["exp", "iat", "iss", "sub"]},
    )

    context = {
        "user_id": claims.get("sub", ""),
        "email": claims.get("email", ""),
        "scope": claims.get("scope", "") if isinstance(claims.get("scope"), str) else "",
    }
    return _policy(context["user_id"] or "user", "Allow", event["methodArn"], context)
