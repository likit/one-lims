"""added annoucement model

Revision ID: 850f202a2940
Revises: 3f59dd726ca4
Create Date: 2020-03-30 03:43:00.497460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '850f202a2940'
down_revision = '3f59dd726ca4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('announcements',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('detail', sa.String(), nullable=False),
    sa.Column('added_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('announcements')
    # ### end Alembic commands ###