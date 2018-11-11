"""added foreign keys

Revision ID: 44549e5a6ac2
Revises: 8b7e8f1f6a4b
Create Date: 2018-11-11 14:22:27.098250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44549e5a6ac2'
down_revision = '8b7e8f1f6a4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_index('id', table_name='revisions')
    op.create_foreign_key(None, 'revisions', 'revision_type', ['revision_type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_constraint(None, 'revisions', type_='foreignkey')
    #op.create_index('id', 'revisions', ['id'], unique=True)
    # ### end Alembic commands ###
    pass
