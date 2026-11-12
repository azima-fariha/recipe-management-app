import logging

import auth
import jwt
from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)


async def require_ownership(user_id: str, authorization: str | None = Header(default=None)) -> str:
    """Enforce Ownership (see GLOSSARY.md) on any route with `user_id` in its path.

    Rejects with 401 when the Authorization header is missing or carries an
    invalid/expired Access Token, and with 403 when the token's subject does
    not match the `user_id` in the path. On success, the route behaves exactly
    as it does today.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization[len("Bearer ") :]
    try:
        subject = auth.decode_access_token(token)
    except jwt.PyJWTError as exc:
        logger.warning("Rejecting request with invalid/expired access token: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if subject != str(user_id):
        logger.warning("Rejecting request: token subject %s does not own user_id %s", subject, user_id)
        raise HTTPException(status_code=403, detail="Token does not grant access to this user")

    return subject
