import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.pacs_models import Patient, Study, Image
from app.core.s3_client import upload_file, create_bucket_if_not_exists, generate_presigned_url
from app.core.sms_client import send_sms
from app.core.config import settings
from app.api.deps import get_current_user_payload

BUCKET_NAME = "pacs-images"

router = APIRouter()

@router.post("/", status_code=201)
async def upload_study(
    patient_full_name: str = Form(...),
    patient_national_id: str = Form(...),
    patient_phone_number: str = Form(...),
    study_description: str = Form(...),
    image_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    token_payload: dict = Depends(get_current_user_payload),
):
    # Ensure bucket exists
    create_bucket_if_not_exists(BUCKET_NAME)

    # Find or create patient
    result = await db.execute(select(Patient).where(Patient.national_id == patient_national_id))
    patient = result.scalar_one_or_none()
    if not patient:
        patient = Patient(
            full_name=patient_full_name,
            national_id=patient_national_id,
            phone_number=patient_phone_number,
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)

    # Create study
    study = Study(
        patient_id=patient.id,
        clinic_id=uuid.uuid4(),  # Placeholder, should come from context
        description=study_description,
        study_date=datetime.utcnow(),
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)

    # Prepare upload
    object_name = f"{uuid.uuid4()}_{image_file.filename}"
    try:
        await image_file.seek(0)
        upload_file(image_file.file, BUCKET_NAME, object_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")

    # Create image record
    image = Image(
        study_id=study.id,
        object_name=object_name,
        file_format=image_file.content_type or "unknown",
        upload_timestamp=datetime.utcnow(),
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)

    return {
        "patient_id": str(patient.id),
        "study_id": str(study.id),
        "image_id": str(image.id),
        "object_name": object_name,
    }


@router.post("/{study_id}/send-link", status_code=200)
async def send_study_link(
    study_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    token_payload: dict = Depends(get_current_user_payload),
):
    # Fetch study
    study = (await db.execute(select(Study).where(Study.id == study_id))).scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    # Fetch patient
    patient = (await db.execute(select(Patient).where(Patient.id == study.patient_id))).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # Fetch images
    images = (await db.execute(select(Image).where(Image.study_id == study_id))).scalars().all()
    if not images:
        raise HTTPException(status_code=404, detail="No images found for this study")
    # Generate presigned URLs
    links = []
    for img in images:
        url = generate_presigned_url(BUCKET_NAME, img.object_name)
        links.append(url)
    # Compose message
    msg = f"Dear {patient.full_name}, your medical images are available:\n" + "\n".join(links)
    # Send SMS (placeholder)
    await send_sms(patient.phone_number, msg)
    return {"status": "sms_sent_successfully"}
