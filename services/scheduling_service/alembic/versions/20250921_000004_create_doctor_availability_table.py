"""create doctor_availability table

Revision ID: 20250921_000004
Revises: 20250921_000003
Create Date: 2025-09-21 00:18:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20250921_000004'
down_revision: Union[str, None] = '20250921_000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create doctor_availability table if it doesn't exist
    if 'doctor_availability' not in existing_tables:
        op.create_table(
            'doctor_availability',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.Time(timezone=False), nullable=False),
            sa.Column('end_time', sa.Time(timezone=False), nullable=False),
        )
        op.create_index('ix_doctor_availability_doctor_id', 'doctor_availability', ['doctor_id'])


def downgrade() -> None:
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop doctor_availability table and index if they exist
    if 'doctor_availability' in existing_tables:
        try:
            op.drop_index('ix_doctor_availability_doctor_id', table_name='doctor_availability')
        except Exception:
            pass  # Index might not exist
        op.drop_table('doctor_availability')

