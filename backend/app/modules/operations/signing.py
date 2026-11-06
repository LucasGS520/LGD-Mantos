import hashlib
import hmac
import json

from app.core.config import settings


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()


def sign(candidate, revision):
    return hmac.new(
        settings.APP_SECRET.encode(), (str(revision) + digest(candidate)).encode(), hashlib.sha256
    ).hexdigest()
