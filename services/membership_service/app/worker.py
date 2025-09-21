import asyncio
import json
import uuid
from typing import Final

from redis.asyncio import from_url as redis_from_url

from app.core.config import settings
from app.db.session import async_session, engine, Base
from app.crud.clinic_member_crud import create_member_admin

CHANNEL: Final = "yakhteh_events"


async def _handle_workspace_created(message: dict) -> None:
    try:
        clinic_id = uuid.UUID(str(message["clinic_id"]))
        user_id = uuid.UUID(str(message["user_id"]))
    except Exception:
        return

    async with async_session() as db:
        await create_member_admin(db, clinic_id=clinic_id, user_id=user_id)


async def run_worker() -> None:
    # Ensure tables exist if migrations haven't run
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    r = redis_from_url(settings.redis_url, decode_responses=True)
    try:
        pubsub = r.pubsub()
        await pubsub.subscribe(CHANNEL)
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            try:
                payload = json.loads(msg.get("data", "{}"))
            except json.JSONDecodeError:
                continue
            if payload.get("event_type") == "WORKSPACE_CREATED":
                await _handle_workspace_created(payload)
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())

