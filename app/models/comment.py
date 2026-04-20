from datetime import datetime
from ..extensions import db


class Comment(db.Model):
    """
    Комментарий — может быть привязан к снимку (photo_id)
    или к текстовому посту (post_id). Ровно одно из двух должно быть заполнено.
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)

    # nullable=True — комментарий может относиться к посту, а не к снимку
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=True)
    post_id  = db.Column(db.Integer, db.ForeignKey('posts.id'),  nullable=True)

    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    text      = db.Column(db.String(500), nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Comment {self.id}>'
