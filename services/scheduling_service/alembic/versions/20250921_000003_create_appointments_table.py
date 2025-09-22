"""create appointments table

Revision ID: 20250921_000003
Revises:
Create Date: 2025-09-21 00:10:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20250921_000003'

down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type if it doesn't exist
    appointment_status_enum = postgresql.ENUM('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW', name='appointmentstatus', create_type=False)
    appointment_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create appointments table if it doesn't exist
    if 'appointments' not in existing_tables:
        op.create_table(
            'appointments',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('patient_name', sa.String(length=255), nullable=False),
            sa.Column('patient_contact_details', sa.String(length=255), nullable=False),
            sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('clinic_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('status', sa.Enum('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW', name='appointmentstatus', create_type=False), nullable=False, server_default='SCHEDULED'),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )
        op.create_index('ix_appointments_doctor_id', 'appointments', ['doctor_id'])
        op.create_index('ix_appointments_clinic_id', 'appointments', ['clinic_id'])


def downgrade() -> None:
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop appointments table and indexes if they exist
    if 'appointments' in existing_tables:
        try:
            op.drop_index('ix_appointments_clinic_id', table_name='appointments')
        except Exception:
            pass  # Index might not exist
        try:
            op.drop_index('ix_appointments_doctor_id', table_name='appointments')
        except Exception:
            pass  # Index might not exist
        op.drop_table('appointments')
    
    # Drop enum type if it exists
    appointment_status_enum = postgresql.ENUM(name='appointmentstatus')
    appointment_status_enum.drop(op.get_bind(), checkfirst=True)

