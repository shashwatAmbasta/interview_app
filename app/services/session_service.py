import json
import time

import redis

from app.core.config import settings


class SessionStore:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    def is_available(self) -> bool:
        try:
            self.client.ping()
            return True
        except redis.RedisError:
            return False

    def require_available(self) -> None:
        if not self.is_available():
            raise RuntimeError("Redis session store is unavailable")

    def create(self, token: str, user_id: int) -> None:
        self.client.setex(
            f"session:{token}",
            settings.session_ttl_seconds,
            json.dumps({"user_id": user_id, "last_seen": time.time()}),
        )

    def delete(self, token: str) -> None:
        self.client.delete(f"session:{token}")

    def exists(self, token: str) -> bool:
        return bool(self.client.exists(f"session:{token}"))

    def save_interview(self, interview_id: str, payload: dict) -> None:
        self.client.setex(f"interview:{interview_id}", settings.session_ttl_seconds, json.dumps(payload))

    def get_interview(self, interview_id: str) -> dict | None:
        raw = self.client.get(f"interview:{interview_id}")
        return json.loads(raw) if raw else None


session_store = SessionStore()
