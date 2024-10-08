"""Added admin role models for Admin portal

Revision ID: acfa7d71e156
Revises: 5df11a22d4ca
Create Date: 2023-06-06 15:33:30.163285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acfa7d71e156'
down_revision = '5df11a22d4ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('role_change_log_role_id_fkey', 'role_change_log', type_='foreignkey')
    op.create_foreign_key('role_change_log_admin_role_id_fkey', 'role_change_log', 'admin_role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('role_change_log_admin_role_id_fkey', 'role_change_log', type_='foreignkey')
    op.create_foreign_key('role_change_log_role_id_fkey', 'role_change_log', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###
