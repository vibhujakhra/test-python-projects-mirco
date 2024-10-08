"""Added Column is_active in template table

Revision ID: 1a5e9cf78326
Revises: 06f85f9f39a6
Create Date: 2022-09-14 15:51:03.047422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a5e9cf78326'
down_revision = '06f85f9f39a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('templates', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('templates', 'is_active')
    # ### end Alembic commands ###
