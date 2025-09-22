"""create users table

Revision ID: 20250921_000001
Revises: 
Create Date: 2025-09-21 00:00:01.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type if it doesn't exist
    user_role_enum = postgresql.ENUM('doctor', 'clinic_admin', name='userrole', create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create users table if it doesn't exist
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('role', user_role_enum, nullable=False, server_default='doctor'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    # Get connection and check for existing tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop users table and index if they exist
    if 'users' in existing_tables:
        try:
            op.drop_index('ix_email', table_name='users')
        except Exception:
            pass  # Index might not exist
        op.drop_table('users')
    
    # Drop enum type if it exists
    user_role_enum = postgresql.ENUM(name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
