"""added profile id to lab test record model

Revision ID: c6bb243f11bd
Revises: bd6a48eb3148
Create Date: 2024-11-14 08:01:56.077953

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6bb243f11bd'
down_revision = 'bd6a48eb3148'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lab_test_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'lab_test_profiles', ['profile_id'], ['id'])

    with op.batch_alter_table('lab_test_records_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lab_test_records_version', schema=None) as batch_op:
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('lab_test_records', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('profile_id')

    # ### end Alembic commands ###