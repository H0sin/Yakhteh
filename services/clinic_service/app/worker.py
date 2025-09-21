import asyncio
import json
import uuid
from typing import Final

from redis.asyncio import from_url as redis_from_url
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.core.config import settings
from app.db.session import async_session, engine
from app.models.clinic_model import Clinic

CHANNEL: Final[str] = "yakhteh_events"


async def _publish_workspace_created(r, *, clinic_id: str, user_id: str) -> None:
    evt = {"event_type": "WORKSPACE_CREATED", "clinic_id": clinic_id, "user_id": user_id}
    await r.publish(CHANNEL, json.dumps(evt))


async def _handle_user_created(session_factory: async_sessionmaker[AsyncSession], r, message: dict) -> None:
    try:
        user_id = str(message["user_id"])  # may be uuid or str
        workspace_name = str(message["workspace_name"])  # required
        owner_uuid = uuid.UUID(user_id)
    except Exception:
        return

    async with session_factory() as db:
        clinic = Clinic(name=workspace_name, address=None, owner_id=owner_uuid)
        db.add(clinic)
        await db.commit()
        await db.refresh(clinic)

        await _publish_workspace_created(r, clinic_id=str(clinic.id), user_id=str(owner_uuid))


async def run_worker() -> None:
    # Optional: ensure tables exist if migrations haven't run
    async with engine.begin() as conn:
        from app.db.session import Base
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
            event_type = payload.get("event_type")
            if event_type == "USER_CREATED":
                await _handle_user_created(async_session, r, payload)
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())

