"""add username and image url field

Revision ID: f970adb42740
Revises: 
Create Date: 2026-05-26 10:05:53.730145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f970adb42740'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(), nullable=False, server_default='Mujahid'))
    op.add_column('posts', sa.Column('img_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('posts', 'img_url')
    op.drop_column('users', 'username')
