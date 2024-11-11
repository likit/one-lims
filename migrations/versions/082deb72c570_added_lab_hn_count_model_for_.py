"""added Lab HN count model for autogenerating HN

Revision ID: 082deb72c570
Revises: ed92356d40fb
Create Date: 2024-11-11 07:23:34.531452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '082deb72c570'
down_revision = 'ed92356d40fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lab_hn_count',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('lab_customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hn', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lab_customers', schema=None) as batch_op:
        batch_op.drop_column('hn')

    op.drop_table('lab_hn_count')
    # ### end Alembic commands ###