from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.db.session import get_session
from app.models.pacs_models import Study, Patient, Image
from app.core.s3_client import generate_presigned_url
from app.core.sms_client import send_sms

router = APIRouter()

@router.post("/studies/{study_id}/send-link", status_code=200)
async def send_study_link(study_id: UUID, session: AsyncSession = Depends(get_session)):
    # Fetch the study, patient, and images
    result = await session.execute(
        select(Study).where(Study.id == study_id).options(
            # Eager load patient and images
            Study.patient, Study.images
        )
    )
    study = result.scalars().unique().first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    patient = study.patient
    images = study.images
    if not patient or not images:
        raise HTTPException(status_code=404, detail="Patient or images not found for this study")

    # Generate presigned URLs for each image
    links = []
    for image in images:
        url = generate_presigned_url(
            bucket_name="studies",  # Adjust if bucket naming is dynamic
            object_name=image.object_name
        )
        if url:
            links.append(url)
    if not links:
        raise HTTPException(status_code=500, detail="Could not generate any presigned URLs")

    # Construct the message
    message = f"Dear {patient.full_name}, your study images are available at the following link(s):\n" + "\n".join(links)

    # Send SMS (placeholder)
    await send_sms(patient.phone_number, message)

    return {"status": "sms_sent_successfully"}

