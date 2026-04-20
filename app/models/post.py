from datetime import datetime
from ..extensions import db


class Post(db.Model):
    """Текстовый пост — вопрос или совет от пользователя."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # 'question' — вопрос сообществу, 'tip' — совет или лайфхак
    post_type = db.Column(db.String(32), nullable=False, default='question')

    is_hidden = db.Column(db.Boolean, default=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship(
        'Comment',
        foreign_keys='Comment.post_id',
        backref=db.backref('post', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    likes = db.relationship(
        'Like',
        foreign_keys='Like.post_id',
        backref=db.backref('post_ref', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Post {self.post_type}: {self.title[:40]}>'
