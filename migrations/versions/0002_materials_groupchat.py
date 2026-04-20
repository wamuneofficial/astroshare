"""add materials and group chat tables

Revision ID: 0002_materials_groupchat
Revises: 0001_create_all_tables
Create Date: 2026-04-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0002_materials_groupchat'
down_revision = '0001_create_all_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле can_edit_materials к пользователям
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('can_edit_materials', sa.Boolean(), nullable=False, server_default='0')
        )

    # Учебные материалы
    op.create_table('materials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Групповые чаты
    op.create_table('group_chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Участники групповых чатов
    op.create_table('group_chat_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['group_chats.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', 'user_id', name='uq_chat_member')
    )

    # Сообщения в групповых чатах
    op.create_table('group_chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['group_chats.id']),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_group_chat_messages_chat_id', 'group_chat_messages', ['chat_id'])


def downgrade():
    op.drop_index('ix_group_chat_messages_chat_id', table_name='group_chat_messages')
    op.drop_table('group_chat_messages')
    op.drop_table('group_chat_members')
    op.drop_table('group_chats')
    op.drop_table('materials')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('can_edit_materials')
