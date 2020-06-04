"""empty message

Revision ID: d90397ce862d
Revises: 3e7ea9bdacbb
Create Date: 2020-06-04 09:01:51.936241

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd90397ce862d'
down_revision = '3e7ea9bdacbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'tenant',
        sa.Column('tenant_id',
                  sa.Integer(),
                  autoincrement=True,
                  nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('tenant_id'))
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'tenant', ['tenant_id'],
                          ['tenant_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'tenant_id')
    op.drop_table('tenant')
    # ### end Alembic commands ###
