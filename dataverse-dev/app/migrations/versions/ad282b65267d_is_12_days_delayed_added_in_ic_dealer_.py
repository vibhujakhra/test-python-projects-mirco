"""is_12_days_delayed added in ic_dealer_mapping table

Revision ID: ad282b65267d
Revises: 3d566273f42b
Create Date: 2023-05-18 14:47:54.955476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad282b65267d'
down_revision = '3d566273f42b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ic_dealer_mapping', sa.Column('is_12_days_delayed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ic_dealer_mapping', 'is_12_days_delayed')
    # ### end Alembic commands ###
