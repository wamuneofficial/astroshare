from datetime import datetime
from sqlalchemy import or_, and_
from ..extensions import db


class Friendship(db.Model):
    """
    Дружба между двумя пользователями.
    status: 'pending' — запрос отправлен, ждёт ответа
            'accepted' — дружба принята
    """
    __tablename__ = 'friendships'

    id           = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status       = db.Column(db.String(16), nullable=False, default='pending', index=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id],
                                backref=db.backref('sent_friend_requests', lazy='dynamic'))
    addressee = db.relationship('User', foreign_keys=[addressee_id],
                                backref=db.backref('received_friend_requests', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship'),
    )

    @staticmethod
    def between(user_a_id, user_b_id):
        """Возвращает запись дружбы между двумя пользователями или None."""
        return Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == user_a_id,
                     Friendship.addressee_id == user_b_id),
                and_(Friendship.requester_id == user_b_id,
                     Friendship.addressee_id == user_a_id),
            )
        ).first()
