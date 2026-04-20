"""create all tables

Revision ID: 0001_create_all_tables
Revises:
Create Date: 2026-04-20 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_all_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('url', sa.String(length=1024), nullable=True),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_news_published_at', 'news', ['published_at'])
    op.create_index('ix_news_source', 'news', ['source'])

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_filename', sa.String(length=256), nullable=True),
        sa.Column('telescopes', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=128), nullable=True),
        sa.Column('website', sa.String(length=256), nullable=True),
        sa.Column('twitter', sa.String(length=128), nullable=True),
        sa.Column('instagram', sa.String(length=128), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('is_banned', sa.Boolean(), nullable=False),
        sa.Column('email_confirmed', sa.Boolean(), nullable=False),
        sa.Column('email_confirm_token', sa.String(length=256), nullable=True),
        sa.Column('password_reset_token', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    op.create_table('photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=256), nullable=False),
        sa.Column('original_filename', sa.String(length=256), nullable=True),
        sa.Column('thumbnail_filename', sa.String(length=256), nullable=True),
        sa.Column('file_format', sa.String(length=16), nullable=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('observation_date', sa.Date(), nullable=True),
        sa.Column('object_name', sa.String(length=128), nullable=True),
        sa.Column('object_type', sa.String(length=64), nullable=True),
        sa.Column('constellation', sa.String(length=64), nullable=True),
        sa.Column('ra', sa.String(length=32), nullable=True),
        sa.Column('dec', sa.String(length=32), nullable=True),
        sa.Column('telescope', sa.String(length=128), nullable=True),
        sa.Column('focal_length', sa.Integer(), nullable=True),
        sa.Column('camera', sa.String(length=128), nullable=True),
        sa.Column('exposure_time', sa.Float(), nullable=True),
        sa.Column('iso_gain', sa.String(length=32), nullable=True),
        sa.Column('frame_count', sa.Integer(), nullable=True),
        sa.Column('location_name', sa.String(length=128), nullable=True),
        sa.Column('bortle_scale', sa.Integer(), nullable=True),
        sa.Column('tags', sa.String(length=512), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('is_hidden', sa.Boolean(), nullable=False),
        sa.Column('plate_solved', sa.Boolean(), nullable=True),
        sa.Column('plate_solve_data', sa.Text(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_type', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_hidden', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_created_at', 'posts', ['created_at'])

    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=True),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('text', sa.String(length=500), nullable=False),
        sa.Column('is_hidden', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id']),
        sa.ForeignKeyConstraint(['photo_id'], ['photos.id']),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='fk_comments_post_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=True),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['photo_id'], ['photos.id']),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='fk_likes_post_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'photo_id', name='unique_user_photo_like'),
        sa.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like')
    )

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('message', sa.String(length=256), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['photo_id'], ['photos.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

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
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    op.create_table('friendships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('addressee_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['addressee_id'], ['users.id'], name='fk_friendships_addressee'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], name='fk_friendships_requester'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship')
    )
    op.create_index('ix_friendships_status', 'friendships', ['status'])


def downgrade():
    op.drop_table('friendships')
    op.drop_table('messages')
    op.drop_table('notifications')
    op.drop_table('likes')
    op.drop_table('comments')
    op.drop_table('posts')
    op.drop_table('photos')
    op.drop_table('users')
    op.drop_table('news')
