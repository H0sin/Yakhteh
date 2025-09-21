"""create pacs tables (patients, studies, images)

Revision ID: 20250921_000005
Revises:
Create Date: 2025-09-21 00:25:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20250921_000005'

down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # patients
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('national_id', sa.String(length=50), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=False),
    )
    op.create_index('ix_patients_national_id', 'patients', ['national_id'], unique=True)
    op.create_index('ix_patients_phone_number', 'patients', ['phone_number'])

    # studies
    op.create_table(
        'studies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('study_date', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_studies_patient_id', 'studies', ['patient_id'])
    op.create_index('ix_studies_clinic_id', 'studies', ['clinic_id'])

    # images
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('study_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('studies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('object_name', sa.String(length=255), nullable=False),
        sa.Column('file_format', sa.String(length=50), nullable=False),
        sa.Column('upload_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_images_study_id', 'images', ['study_id'])


def downgrade() -> None:
    op.drop_index('ix_images_study_id', table_name='images')
    op.drop_table('images')
    op.drop_index('ix_studies_clinic_id', table_name='studies')
    op.drop_index('ix_studies_patient_id', table_name='studies')
    op.drop_table('studies')
    op.drop_index('ix_patients_phone_number', table_name='patients')
    op.drop_index('ix_patients_national_id', table_name='patients')
    op.drop_table('patients')

