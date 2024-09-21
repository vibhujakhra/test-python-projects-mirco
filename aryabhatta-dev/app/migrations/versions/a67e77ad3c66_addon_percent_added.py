"""addon percent added

Revision ID: a67e77ad3c66
Revises: 7b8848b1301a
Create Date: 2023-02-02 16:25:56.024689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a67e77ad3c66'
down_revision = '7b8848b1301a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('addon_price', sa.Column('addon_percent', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('addon_price', 'addon_percent')
    # ### end Alembic commands ###
