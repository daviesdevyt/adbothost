"""empty message

Revision ID: 1db6feb37ecb
Revises: 8bcba9da2aaa
Create Date: 2023-06-21 19:56:53.586048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1db6feb37ecb'
down_revision = '8bcba9da2aaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('channel_message_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'channel_message_id')
    # ### end Alembic commands ###
