import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic_member_model import ClinicMember, MemberRole


async def create_member_admin(db: AsyncSession, *, clinic_id: uuid.UUID, user_id: uuid.UUID) -> ClinicMember:
    member = ClinicMember(clinic_id=clinic_id, user_id=user_id, role=MemberRole.admin)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member

