"""Add is_admin column to users table

Revision ID: add_is_admin_column
Revises: 939e613fc2f4
Create Date: 2023-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_admin_column'
down_revision: Union[str, None] = '939e613fc2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    # Remove is_admin column from users table
    op.drop_column('users', 'is_admin')
