import json
from typing import Final
from redis.asyncio import from_url as redis_from_url

from app.core.config import settings

CHANNEL: Final[str] = "yakhteh_events"


async def publish_user_created(*, user_id: str, user_email: str, workspace_name: str) -> None:
    r = redis_from_url(settings.redis_url, decode_responses=True)
    try:
        payload = {
            "event_type": "USER_CREATED",
            "user_id": user_id,
            "user_email": user_email,
            "workspace_name": workspace_name,
        }
        await r.publish(CHANNEL, json.dumps(payload))
    finally:
        await r.aclose()

