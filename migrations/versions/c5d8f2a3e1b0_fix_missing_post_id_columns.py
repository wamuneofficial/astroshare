"""fix missing post_id columns in comments and likes

Revision ID: c5d8f2a3e1b0
Revises: b3e9a1f07c42
Create Date: 2026-04-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'c5d8f2a3e1b0'
down_revision = 'b3e9a1f07c42'
branch_labels = None
depends_on = None


def _column_exists(table, column):
    """Проверяем, есть ли колонка в таблице (защита от повторного запуска)."""
    conn = op.get_bind()
    insp = inspect(conn)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols


def upgrade():
    # --- Добавляем post_id в comments (если ещё нет) ---
    with op.batch_alter_table('comments', schema=None) as batch_op:
        if not _column_exists('comments', 'post_id'):
            batch_op.add_column(sa.Column('post_id', sa.Integer(), nullable=True))
        # Делаем photo_id необязательным (комментарий может быть к посту)
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=True)
        # Внешний ключ (batch mode — SQLite-совместимо)
        try:
            batch_op.create_foreign_key('fk_comments_post_id', 'posts', ['post_id'], ['id'])
        except Exception:
            pass  # уже существует

    # --- Добавляем post_id в likes (если ещё нет) ---
    with op.batch_alter_table('likes', schema=None) as batch_op:
        if not _column_exists('likes', 'post_id'):
            batch_op.add_column(sa.Column('post_id', sa.Integer(), nullable=True))
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=True)
        try:
            batch_op.create_unique_constraint(
                'unique_user_post_like', ['user_id', 'post_id'])
        except Exception:
            pass
        try:
            batch_op.create_foreign_key('fk_likes_post_id', 'posts', ['post_id'], ['id'])
        except Exception:
            pass


def downgrade():
    with op.batch_alter_table('likes', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('fk_likes_post_id', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_constraint('unique_user_post_like', type_='unique')
        except Exception:
            pass
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=False)
        try:
            batch_op.drop_column('post_id')
        except Exception:
            pass

    with op.batch_alter_table('comments', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('fk_comments_post_id', type_='foreignkey')
        except Exception:
            pass
        batch_op.alter_column('photo_id', existing_type=sa.INTEGER(), nullable=False)
        try:
            batch_op.drop_column('post_id')
        except Exception:
            pass
