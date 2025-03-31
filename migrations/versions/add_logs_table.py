"""add logs table

Revision ID: add_logs_table
Revises: 4c3730bc904a
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_logs_table'
down_revision = '4c3730bc904a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operation_time', sa.DateTime(), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('operator_name', sa.String(length=100), nullable=False),
        sa.Column('mac_address', sa.String(length=100), nullable=False),
        sa.Column('work_order', sa.String(length=100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('logs')