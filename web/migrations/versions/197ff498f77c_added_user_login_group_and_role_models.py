"""Added user, login, group, and role models

Revision ID: 197ff498f77c
Revises: c7ebb23a675d
Create Date: 2020-05-14 17:56:03.253644

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '197ff498f77c'
down_revision = 'c7ebb23a675d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('email_confirmed_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('first_name', sa.String(length=64), nullable=False),
        sa.Column('last_name', sa.String(length=64), nullable=False),
        sa.Column('address_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_archived', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(
            ['address_id'],
            ['addresses.address_id'],
        ), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
