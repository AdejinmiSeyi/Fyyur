"""empty message

Revision ID: 7bd0b5d49869
Revises: 7bf484a1ee9e
Create Date: 2022-08-29 06:54:36.614067

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7bd0b5d49869'
down_revision = '7bf484a1ee9e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=False))
    op.drop_column('Artist', 'description')
    op.alter_column('Show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=False))
    op.drop_column('Venue', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('description', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.drop_column('Venue', 'seeking_description')
    op.alter_column('Show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.add_column('Artist', sa.Column('description', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
