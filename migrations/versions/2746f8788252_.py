"""empty message

Revision ID: 2746f8788252
Revises: 10b6809efd02
Create Date: 2022-08-21 04:59:09.209096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2746f8788252'
down_revision = '10b6809efd02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###