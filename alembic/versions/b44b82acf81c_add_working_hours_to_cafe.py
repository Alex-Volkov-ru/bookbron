"""add_working_hours_to_cafe

Revision ID: b44b82acf81c
Revises: 3452e17456ab
Create Date: 2026-01-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b44b82acf81c'
down_revision = '3452e17456ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поля рабочего времени в таблицу cafes
    op.add_column('cafes', sa.Column('work_start_time', sa.Time(), nullable=True))
    op.add_column('cafes', sa.Column('work_end_time', sa.Time(), nullable=True))
    op.add_column('cafes', sa.Column('slot_duration_minutes', sa.Integer(), nullable=True, server_default='60'))


def downgrade() -> None:
    op.drop_column('cafes', 'slot_duration_minutes')
    op.drop_column('cafes', 'work_end_time')
    op.drop_column('cafes', 'work_start_time')
