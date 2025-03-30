"""Add answers TEXT column to Score

Revision ID: 8697cff9d503
Revises: bf0ba616938a
Create Date: 2025-03-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8697cff9d503'
down_revision = 'bf0ba616938a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('scores') as batch_op:
        batch_op.add_column(sa.Column('answers', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('scores') as batch_op:
        batch_op.drop_column('answers')

