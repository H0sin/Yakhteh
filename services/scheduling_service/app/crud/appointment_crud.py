from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment_model import Appointment
from app.schemas.appointment_schema import AppointmentCreate


async def create_appointment(db: AsyncSession, payload: AppointmentCreate) -> Appointment:
    appt = Appointment(
        patient_name=payload.patient_name,
        patient_contact_details=payload.patient_contact_details,
        doctor_id=payload.doctor_id,
        clinic_id=payload.clinic_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt

