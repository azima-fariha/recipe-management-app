import datetime
import os

import jwt

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = datetime.timedelta(days=7)


def create_access_token(subject: str) -> str:
    """Mint an Access Token (see GLOSSARY.md) whose subject is the owning user's id."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {"sub": subject, "iat": now, "exp": now + ACCESS_TOKEN_LIFETIME}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """Decode an Access Token and return its subject (the owning user's id).

    Raises jwt.PyJWTError (or a subclass) if the token is malformed, unsigned
    by us, or expired — callers are expected to translate that into a 401.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload["sub"]
