"""merge all migration

Revision ID: 19217d48e99c
Revises: 
Create Date: 2023-01-27 13:17:10.105148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19217d48e99c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aai_membership',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('addon',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agreement_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('bank',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('broker',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('cin', sa.VARCHAR(), nullable=True),
    sa.Column('validity', sa.DATE(), nullable=True),
    sa.Column('irda_license_no', sa.VARCHAR(), nullable=True),
    sa.Column('address', sa.VARCHAR(), nullable=True),
    sa.Column('category', sa.VARCHAR(), nullable=True),
    sa.Column('mobile', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('irda_license_no')
    )
    op.create_table('city_cluster',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('claim_count',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('count', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('claim_year',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('country',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cpa_wavier_reason',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('designation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('financier',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financier_id'), 'financier', ['id'], unique=False)
    op.create_index(op.f('ix_financier_name'), 'financier', ['name'], unique=False)
    op.create_table('fuel_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('geo_extension',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('imt_mapping',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('key_name', sa.VARCHAR(), nullable=True),
    sa.Column('imt_code', sa.VARCHAR(), nullable=False),
    sa.Column('addon_imt_code', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('addon_imt_code'),
    sa.UniqueConstraint('imt_code')
    )
    op.create_table('ncb_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oem',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('policy_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('previous_policy_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('proposer_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('relation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rto_cluster',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rto_zone',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_type', sa.VARCHAR(), nullable=True),
    sa.Column('zone_name', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('salutation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('salutation_type', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('user_role',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vb64_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('no_claim_bonus',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('policy_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['policy_type_id'], ['policy_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('region',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('group_type', sa.VARCHAR(), nullable=True),
    sa.Column('rto_zone_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['rto_zone_id'], ['rto_zone.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehicle_class',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('state',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('group_type', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('zone', sa.VARCHAR(), nullable=True),
    sa.Column('region', sa.Integer(), nullable=True),
    sa.Column('gst_code', sa.VARCHAR(), nullable=True),
    sa.Column('country_id', sa.Integer(), nullable=True),
    sa.Column('is_union_territory', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['country.id'], ),
    sa.ForeignKeyConstraint(['region'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehicle_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('vehicle_class_id', sa.Integer(), nullable=True),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.ForeignKeyConstraint(['vehicle_class_id'], ['vehicle_class.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pa_cover',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.VARCHAR(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('vehicle_type', sa.Integer(), nullable=True),
    sa.Column('vehicle_class_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['vehicle_class_id'], ['vehicle_class.id'], ),
    sa.ForeignKeyConstraint(['vehicle_type'], ['vehicle_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehicle_cover',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('policy_type_id', sa.Integer(), nullable=True),
    sa.Column('od_tenure', sa.Integer(), nullable=True),
    sa.Column('tp_tenure', sa.Integer(), nullable=True),
    sa.Column('full_name', sa.VARCHAR(), nullable=True),
    sa.Column('vehicle_type_id', sa.Integer(), nullable=True),
    sa.Column('vehicle_class_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['policy_type_id'], ['policy_type.id'], ),
    sa.ForeignKeyConstraint(['vehicle_class_id'], ['vehicle_class.id'], ),
    sa.ForeignKeyConstraint(['vehicle_type_id'], ['vehicle_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehicle_model',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('vehicle_class_id', sa.Integer(), nullable=True),
    sa.Column('vehicle_type_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.ForeignKeyConstraint(['vehicle_class_id'], ['vehicle_class.id'], ),
    sa.ForeignKeyConstraint(['vehicle_type_id'], ['vehicle_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('voluntary_deductible',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.VARCHAR(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('vehicle_class_id', sa.Integer(), nullable=True),
    sa.Column('vehicle_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['vehicle_class_id'], ['vehicle_class.id'], ),
    sa.ForeignKeyConstraint(['vehicle_type_id'], ['vehicle_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city_cluster_city_mapping',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('city_cluster_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['city_cluster_id'], ['city_cluster.id'], ),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dealer',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('dealer_name', sa.VARCHAR(), nullable=False),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('dealer_code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dealer_code')
    )
    op.create_table('new_vehicle_cover',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('is_od_expired', sa.Boolean(), nullable=True),
    sa.Column('is_tp_expired', sa.Boolean(), nullable=True),
    sa.Column('od_tp_condition', sa.Enum('OD_EXPIRY_EQ_TP_EXPIRY', 'OD_EXPIRY_GT_TP_EXPIRY', 'OD_EXPIRY_LT_TP_EXPIRY', 'OD_EXPIRY_DIFF_TP_EXPIRY_EQ_THREE', 'STANDALONE_OD', 'STANDALONE_TP', name='odtpconditions'), nullable=False),
    sa.Column('current_date_conditions', sa.Enum('CURRENT_DATE_EQ_TP_EXPIRY', 'CURRENT_DATE_GT_TP_EXPIRY', 'CURRENT_DATE_LT_TP_EXPIRY', 'CURRENT_DATE_EQ_OD_EXPIRY', 'CURRENT_DATE_GT_OD_EXPIRY', 'CURRENT_DATE_LT_OD_EXPIRY', name='currentdateconditions'), nullable=True),
    sa.Column('vehicle_cover_id', sa.Integer(), nullable=True),
    sa.Column('old_vehicle_cover_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['old_vehicle_cover_id'], ['vehicle_cover.id'], ),
    sa.ForeignKeyConstraint(['vehicle_cover_id'], ['vehicle_cover.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pincode',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rto',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('rto_zone_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['rto_zone_id'], ['rto_zone.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('variant',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('variant_code', sa.VARCHAR(), nullable=True),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('cubic_capacity', sa.Integer(), nullable=True),
    sa.Column('kilowatt_range', sa.Float(), nullable=True),
    sa.Column('seating_capacity', sa.Integer(), nullable=True),
    sa.Column('fuel_type_id', sa.Integer(), nullable=True),
    sa.Column('license_carrying_capacity', sa.Integer(), nullable=True),
    sa.Column('carrying_capacity', sa.Integer(), nullable=True),
    sa.Column('body_type', sa.VARCHAR(), nullable=True),
    sa.Column('is_bifuel', sa.Boolean(), nullable=True),
    sa.Column('segment_type', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_type.id'], ),
    sa.ForeignKeyConstraint(['model_id'], ['vehicle_model.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('variant_code')
    )
    op.create_table('vehicle_coverage_vehicle_type',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vehicle_cover_id', sa.Integer(), nullable=True),
    sa.Column('vehicle_type_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['vehicle_cover_id'], ['vehicle_cover.id'], ),
    sa.ForeignKeyConstraint(['vehicle_type_id'], ['vehicle_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dealer_person',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dealer_person_name', sa.VARCHAR(), nullable=False),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('dealer_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['dealer_id'], ['dealer.id'], ),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dealer_id')
    )
    op.create_table('insurer',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('code', sa.VARCHAR(), nullable=False),
    sa.Column('ic_address_1', sa.VARCHAR(), nullable=True),
    sa.Column('ic_address_2', sa.VARCHAR(), nullable=True),
    sa.Column('ic_address_3', sa.VARCHAR(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('pincode_id', sa.Integer(), nullable=True),
    sa.Column('landline_no', sa.VARCHAR(), nullable=True),
    sa.Column('helpdesk_no', sa.VARCHAR(), nullable=True),
    sa.Column('ic_email', sa.VARCHAR(), nullable=True),
    sa.Column('website_address', sa.VARCHAR(), nullable=True),
    sa.Column('service_tax_code_no', sa.VARCHAR(), nullable=True),
    sa.Column('service_tax_registration_no', sa.VARCHAR(), nullable=True),
    sa.Column('cin', sa.VARCHAR(), nullable=True),
    sa.Column('uin', sa.VARCHAR(), nullable=True),
    sa.Column('servicing_office_address', sa.VARCHAR(), nullable=True),
    sa.Column('registered_office_address', sa.VARCHAR(), nullable=True),
    sa.Column('hsn_sac', sa.VARCHAR(), nullable=True),
    sa.Column('irda_registration_no', sa.VARCHAR(), nullable=False),
    sa.Column('insurer_logo', sa.VARCHAR(), nullable=True),
    sa.Column('pan_number', sa.VARCHAR(), nullable=True),
    sa.Column('gstin_number', sa.VARCHAR(), nullable=True),
    sa.Column('description_of_service', sa.VARCHAR(), nullable=True),
    sa.Column('place_of_supply', sa.VARCHAR(), nullable=True),
    sa.Column('invoice_number', sa.VARCHAR(), nullable=True),
    sa.Column('digital_signature', sa.VARCHAR(), nullable=True),
    sa.Column('authorized_signatory_name', sa.VARCHAR(), nullable=True),
    sa.Column('authorized_signatory_designation', sa.VARCHAR(), nullable=True),
    sa.Column('limitations_as_to_us', sa.VARCHAR(), nullable=True),
    sa.Column('drivers_clause', sa.VARCHAR(), nullable=True),
    sa.Column('grievance_clause', sa.VARCHAR(), nullable=True),
    sa.Column('disclaimer', sa.VARCHAR(), nullable=True),
    sa.Column('important_notice', sa.VARCHAR(), nullable=True),
    sa.Column('note', sa.VARCHAR(), nullable=True),
    sa.Column('fastag_clause', sa.VARCHAR(), nullable=True),
    sa.Column('puc_clause', sa.VARCHAR(), nullable=True),
    sa.Column('limits_of_liability_clause', sa.VARCHAR(), nullable=True),
    sa.Column('compulsory_deductible', sa.Integer(), nullable=True),
    sa.Column('cpa_sum_insured_for_liability_clause', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('agency_name', sa.VARCHAR(), nullable=True),
    sa.Column('agency_code', sa.VARCHAR(), nullable=True),
    sa.Column('deposit_bank_id', sa.Integer(), nullable=True),
    sa.Column('deposit_account_no', sa.VARCHAR(), nullable=True),
    sa.Column('account_type_id', sa.Integer(), nullable=True),
    sa.Column('payment_collection_address', sa.VARCHAR(), nullable=True),
    sa.Column('payment_collection_landline_no', sa.VARCHAR(), nullable=True),
    sa.Column('payment_collection_mobile_no', sa.VARCHAR(), nullable=True),
    sa.Column('transfer_fee', sa.Integer(), nullable=True),
    sa.Column('endorsment_charge', sa.Integer(), nullable=True),
    sa.Column('endorsment_status', sa.Boolean(), nullable=True),
    sa.Column('cancellation_email', sa.VARCHAR(), nullable=True),
    sa.Column('claim_email', sa.VARCHAR(), nullable=True),
    sa.Column('endorsment_email', sa.VARCHAR(), nullable=True),
    sa.Column('ncb_carry_forward_email', sa.VARCHAR(), nullable=True),
    sa.Column('break_in_case_email', sa.VARCHAR(), nullable=True),
    sa.Column('master_email', sa.VARCHAR(), nullable=True),
    sa.Column('user_obj_id', sa.VARCHAR(), nullable=True),
    sa.Column('cms_bank_name_id', sa.Integer(), nullable=True),
    sa.Column('cms_client_code', sa.VARCHAR(), nullable=True),
    sa.Column('is_quotation_integrated', sa.Boolean(), nullable=True),
    sa.Column('is_proposal_integrated', sa.Boolean(), nullable=True),
    sa.Column('is_policy_integrated', sa.Boolean(), nullable=True),
    sa.Column('is_payment_integrated', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['account_type_id'], ['account_type.id'], ),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['cms_bank_name_id'], ['bank.id'], ),
    sa.ForeignKeyConstraint(['deposit_bank_id'], ['bank.id'], ),
    sa.ForeignKeyConstraint(['pincode_id'], ['pincode.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cin'),
    sa.UniqueConstraint('irda_registration_no'),
    sa.UniqueConstraint('uin')
    )
    op.create_table('rto_cluster_rto_mapping',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('rto_id', sa.Integer(), nullable=True),
    sa.Column('rto_cluster_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['rto_cluster_id'], ['rto_cluster.id'], ),
    sa.ForeignKeyConstraint(['rto_id'], ['rto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sub_variant',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tone', sa.VARCHAR(), nullable=True),
    sa.Column('color', sa.VARCHAR(), nullable=True),
    sa.Column('variant_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['variant_id'], ['variant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bundle',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('insurer_id', sa.Integer(), nullable=True),
    sa.Column('code', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['insurer_id'], ['insurer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ex_showroom_price',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('city', sa.Integer(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('variant_id', sa.Integer(), nullable=True),
    sa.Column('sub_variant_id', sa.Integer(), nullable=True),
    sa.Column('charges_price', sa.Integer(), nullable=True),
    sa.Column('exShowRoomPrice', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['city'], ['city.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.ForeignKeyConstraint(['sub_variant_id'], ['sub_variant.id'], ),
    sa.ForeignKeyConstraint(['variant_id'], ['variant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('insurer_local_office',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('insurer_id', sa.Integer(), nullable=True),
    sa.Column('local_office_code', sa.VARCHAR(), nullable=True),
    sa.Column('gst_in', sa.VARCHAR(), nullable=True),
    sa.Column('address_1', sa.VARCHAR(), nullable=True),
    sa.Column('address_2', sa.VARCHAR(), nullable=True),
    sa.Column('address_3', sa.VARCHAR(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('pincode_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('landline_no', sa.VARCHAR(), nullable=True),
    sa.Column('mobile_no', sa.VARCHAR(), nullable=True),
    sa.Column('helpdesk_no', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['insurer_id'], ['insurer.id'], ),
    sa.ForeignKeyConstraint(['pincode_id'], ['pincode.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oem_insurer',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('insurer_id', sa.Integer(), nullable=True),
    sa.Column('oem', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['insurer_id'], ['insurer.id'], ),
    sa.ForeignKeyConstraint(['oem'], ['oem.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sales_manager',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('sales_manager_name', sa.VARCHAR(), nullable=False),
    sa.Column('oem_id', sa.Integer(), nullable=True),
    sa.Column('dealer_id', sa.Integer(), nullable=True),
    sa.Column('dealer_person_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['dealer_id'], ['dealer.id'], ),
    sa.ForeignKeyConstraint(['dealer_person_id'], ['dealer_person.id'], ),
    sa.ForeignKeyConstraint(['oem_id'], ['oem.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dealer_id')
    )
    op.create_table('addon_bundle',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('bundle_id', sa.Integer(), nullable=True),
    sa.Column('addon_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['addon_id'], ['addon.id'], ),
    sa.ForeignKeyConstraint(['bundle_id'], ['bundle.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ic_dealer_mapping',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('insurer_id', sa.Integer(), nullable=True),
    sa.Column('dealer_id', sa.Integer(), nullable=True),
    sa.Column('local_office_id', sa.Integer(), nullable=True),
    sa.Column('payment_mode_code_new', sa.Integer(), nullable=True),
    sa.Column('payment_mode_code_renew', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['dealer_id'], ['dealer.id'], ),
    sa.ForeignKeyConstraint(['insurer_id'], ['insurer.id'], ),
    sa.ForeignKeyConstraint(['local_office_id'], ['insurer_local_office.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ic_dealer_mapping')
    op.drop_table('addon_bundle')
    op.drop_table('sales_manager')
    op.drop_table('oem_insurer')
    op.drop_table('insurer_local_office')
    op.drop_table('ex_showroom_price')
    op.drop_table('bundle')
    op.drop_table('sub_variant')
    op.drop_table('rto_cluster_rto_mapping')
    op.drop_table('insurer')
    op.drop_table('dealer_person')
    op.drop_table('vehicle_coverage_vehicle_type')
    op.drop_table('variant')
    op.drop_table('rto')
    op.drop_table('pincode')
    op.drop_table('new_vehicle_cover')
    op.drop_table('dealer')
    op.drop_table('city_cluster_city_mapping')
    op.drop_table('voluntary_deductible')
    op.drop_table('vehicle_model')
    op.drop_table('vehicle_cover')
    op.drop_table('pa_cover')
    op.drop_table('city')
    op.drop_table('vehicle_type')
    op.drop_table('state')
    op.drop_table('vehicle_class')
    op.drop_table('region')
    op.drop_table('no_claim_bonus')
    op.drop_table('vb64_type')
    op.drop_table('user_role')
    op.drop_table('transaction_type')
    op.drop_table('salutation')
    op.drop_table('rto_zone')
    op.drop_table('rto_cluster')
    op.drop_table('relation')
    op.drop_table('proposer_type')
    op.drop_table('previous_policy_type')
    op.drop_table('policy_type')
    op.drop_table('oem')
    op.drop_table('ncb_type')
    op.drop_table('imt_mapping')
    op.drop_table('geo_extension')
    op.drop_table('fuel_type')
    op.drop_index(op.f('ix_financier_name'), table_name='financier')
    op.drop_index(op.f('ix_financier_id'), table_name='financier')
    op.drop_table('financier')
    op.drop_table('designation')
    op.drop_table('cpa_wavier_reason')
    op.drop_table('country')
    op.drop_table('claim_year')
    op.drop_table('claim_count')
    op.drop_table('city_cluster')
    op.drop_table('broker')
    op.drop_table('bank')
    op.drop_table('agreement_type')
    op.drop_table('addon')
    op.drop_table('account_type')
    op.drop_table('aai_membership')
    # ### end Alembic commands ###
