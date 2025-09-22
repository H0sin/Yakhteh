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
    # Create enum type if it doesn't exist
    subscription_status_enum = postgresql.ENUM('free', 'premium', 'expired', name='subscriptionstatus', create_type=False)
    subscription_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create clinics table if it doesn't exist
    if 'clinics' not in existing_tables:
        op.create_table(
            'clinics',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('address', sa.String(length=500), nullable=True),
            sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('subscription_status', sa.Enum('free', 'premium', 'expired', name='subscriptionstatus', create_type=False), nullable=False, server_default='free'),
        )
        op.create_index('ix_clinics_name', 'clinics', ['name'])
        op.create_index('ix_clinics_owner_id', 'clinics', ['owner_id'])


def downgrade() -> None:
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop clinics table and indexes if they exist
    if 'clinics' in existing_tables:
        try:
            op.drop_index('ix_clinics_owner_id', table_name='clinics')
        except Exception:
            pass  # Index might not exist
        try:
            op.drop_index('ix_clinics_name', table_name='clinics')
        except Exception:
            pass  # Index might not exist
        op.drop_table('clinics')
    
    # Drop enum type if it exists
    subscription_status_enum = postgresql.ENUM(name='subscriptionstatus')
    subscription_status_enum.drop(op.get_bind(), checkfirst=True)
