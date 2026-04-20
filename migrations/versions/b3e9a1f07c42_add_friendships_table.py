"""add friendships table

Revision ID: b3e9a1f07c42
Revises: 59317f316362
Create Date: 2026-04-20 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3e9a1f07c42'
down_revision = '59317f316362'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('friendships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('addressee_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['addressee_id'], ['users.id'],
                                name='fk_friendships_addressee'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'],
                                name='fk_friendships_requester'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship')
    )
    with op.batch_alter_table('friendships', schema=None) as batch_op:
        batch_op.create_index('ix_friendships_status', ['status'], unique=False)


def downgrade():
    with op.batch_alter_table('friendships', schema=None) as batch_op:
        batch_op.drop_index('ix_friendships_status')
    op.drop_table('friendships')
