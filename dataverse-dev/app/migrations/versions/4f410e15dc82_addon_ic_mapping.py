"""addon-ic-mapping

Revision ID: 4f410e15dc82
Revises: 372ca06bcba5
Create Date: 2023-02-13 16:39:06.718506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f410e15dc82'
down_revision = '372ca06bcba5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('addon', sa.Column('insurer_code', sa.VARCHAR(), nullable=True))
    op.add_column('addon', sa.Column('uin', sa.VARCHAR(), nullable=True))
    op.create_unique_constraint(None, 'addon', ['uin'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'addon', type_='unique')
    op.drop_column('addon', 'uin')
    op.drop_column('addon', 'insurer_code')
    # ### end Alembic commands ###
