"""init_tables

Revision ID: c37325e30440
Revises: 
Create Date: 2025-03-06 17:50:37.803243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c37325e30440'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('e_statione',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mac_id', sa.String(length=50), nullable=False),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('location', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('connection_status', sa.Boolean(), nullable=True),
    sa.Column('last_connected', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mac_id')
    )
    op.create_table('light_strip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('strip_id', sa.String(length=80), nullable=False),
    sa.Column('mac_address', sa.String(length=80), nullable=False),
    sa.Column('work_order', sa.String(length=100), nullable=False),
    sa.Column('last_estatione_mac', sa.String(length=80), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('strip_id')
    )
    op.create_table('system_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('check_lightstrip_duplicate', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('department', sa.String(length=80), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('department', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('user')
    op.drop_table('system_config')
    op.drop_table('light_strip')
    op.drop_table('e_statione')
    # ### end Alembic commands ###
