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
    op.drop_index('ix_doctor_availability_doctor_id', table_name='doctor_availability')
    op.drop_table('doctor_availability')

