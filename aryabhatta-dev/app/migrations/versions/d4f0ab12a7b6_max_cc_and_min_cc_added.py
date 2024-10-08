"""max_cc and min_cc added

Revision ID: d4f0ab12a7b6
Revises: b04ecd0a7c18
Create Date: 2023-01-13 16:50:06.094387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f0ab12a7b6'
down_revision = '61d22f97f486'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('od_rate', sa.Column('min_kw', sa.Integer(), nullable=True))
    op.add_column('od_rate', sa.Column('max_kw', sa.Integer(), nullable=True))
    op.add_column('tp_rate', sa.Column('min_kw', sa.Integer(), nullable=True))
    op.add_column('tp_rate', sa.Column('max_kw', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tp_rate', 'max_kw')
    op.drop_column('tp_rate', 'min_kw')
    op.drop_column('od_rate', 'max_kw')
    op.drop_column('od_rate', 'min_kw')
    # ### end Alembic commands ###
