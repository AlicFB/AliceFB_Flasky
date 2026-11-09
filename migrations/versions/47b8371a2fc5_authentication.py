"""authentication

Revision ID: 47b8371a2fc5
Revises: 38c4e85512a9
Create Date: 2026-11-09 13:35:40.641552

"""

revision = '47b8371a2fc5'
down_revision = '38c4e85512a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=256), nullable=True))
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'confirmed')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
