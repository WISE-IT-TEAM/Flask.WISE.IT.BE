"""Thumbnail Column Delete

Revision ID: adac62538055
Revises: 0db80ed0ffff
Create Date: 2024-07-12 22:07:41.936843

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'adac62538055'
down_revision = '0db80ed0ffff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_column('thumbnail')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thumbnail', mysql.VARCHAR(length=300), nullable=True))

    # ### end Alembic commands ###
