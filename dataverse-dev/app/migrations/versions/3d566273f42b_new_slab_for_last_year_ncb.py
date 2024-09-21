"""new slab for last year ncb

Revision ID: 3d566273f42b
Revises: c4d49f0997e7
Create Date: 2023-05-04 13:26:54.457412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d566273f42b'
down_revision = 'c4d49f0997e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('no_claim_bonus', sa.Column('new_slab_value', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('no_claim_bonus', 'new_slab_value')
    # ### end Alembic commands ###
