"""create clinics table

Revision ID: 20250921_000002
Revises: 
Create Date: 2025-09-21 00:05:01.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20250921_000002'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'clinics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_status', sa.Enum('free', 'premium', 'expired', name='subscriptionstatus'), nullable=False, server_default='free'),
    )
    op.create_index('ix_clinics_name', 'clinics', ['name'])
    op.create_index('ix_clinics_owner_id', 'clinics', ['owner_id'])


def downgrade() -> None:
    op.drop_index('ix_clinics_owner_id', table_name='clinics')
    op.drop_index('ix_clinics_name', table_name='clinics')
    op.drop_table('clinics')
