"""add messages table

Revision ID: 59317f316362
Revises: ca412f572558
Create Date: 2026-04-20 12:54:01.904341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59317f316362'
down_revision = 'ca412f572558'
branch_labels = None
depends_on = None


def upgrade():
    # Создаём таблицу личных сообщений
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=256), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], name='fk_messages_recipient'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], name='fk_messages_sender'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index('ix_messages_created_at', ['created_at'], unique=False)

    # Добавляем post_id в comments (если колонки ещё нет)
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('post_id', sa.Integer(), nullable=True))
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_foreign_key('fk_comments_post_id', 'posts', ['post_id'], ['id'])

    # Добавляем post_id в likes (если колонки ещё нет)
    with op.batch_alter_table('likes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('post_id', sa.Integer(), nullable=True))
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_unique_constraint('unique_user_post_like', ['user_id', 'post_id'])
        batch_op.create_foreign_key('fk_likes_post_id', 'posts', ['post_id'], ['id'])


def downgrade():
    with op.batch_alter_table('likes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_likes_post_id', type_='foreignkey')
        batch_op.drop_constraint('unique_user_post_like', type_='unique')
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_column('post_id')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comments_post_id', type_='foreignkey')
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_column('post_id')

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index('ix_messages_created_at')

    op.drop_table('messages')
