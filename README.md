# ARO Analytics API — REST API + Lambda Authorizer (Clerk)

- API Gateway **REST API**
- **Lambda Authorizer (TOKEN)** verifies Clerk JWT via JWKS
- DB: MySQL (RDS)
- CI/CD: GitHub Actions + flake8 + Serverless deploy

## Endpoints
- `GET /health` — public
- `GET /reports` — protected (Lambda authorizer)

## Env Vars (GitHub Secrets / local shell)
JWT_AUDIENCE=aro-api
CLERK_ISSUER_URL=https://YOUR-CLERK-DOMAIN/
CLERK_JWKS_URL=https://YOUR-CLERK-DOMAIN/.well-known/jwks.json
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

## Clerk token
Create a JWT template with:
- `aud` = `blue-keys-api` (matches `JWT_AUDIENCE`)
- include `org_id`, `email`, and optional `scope`, `roles`

## Deploy
npm i -g serverless serverless-python-requirements
pip install -r requirements.txt
serverless deploy --stage dev

## Notes
- In REST API, Lambda authorizer context is available at:
  `event.requestContext.authorizer`