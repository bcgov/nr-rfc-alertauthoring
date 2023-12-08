"""initial schema

Revision ID: V1
Revises: 
Create Date: 2023-12-06 12:10:32.680706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'V2'
down_revision: Union[str, None] = 'V1'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=1000000, cycle=False, cache=1), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    schema='py_api'
    )
    op.create_table('user_addresses',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=1000000, cycle=False, cache=1), nullable=False),
    sa.Column('street', sa.String(length=50), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=False),
    sa.Column('zip_code', sa.String(length=10), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['py_api.user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='py_api'
    )
    # ### end Alembic commands ###


    


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_addresses', schema='py_api')
    op.drop_table('user', schema='py_api')
    # ### end Alembic commands ###
