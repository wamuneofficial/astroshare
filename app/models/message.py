from datetime import datetime
from ..extensions import db


class Message(db.Model):
    """Личное сообщение между двумя пользователями."""
    __tablename__ = 'messages'

    id           = db.Column(db.Integer, primary_key=True)
    sender_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject      = db.Column(db.String(256), nullable=False)
    body         = db.Column(db.Text, nullable=False)
    is_read      = db.Column(db.Boolean, default=False, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Связи: явно указываем foreign_keys, так как их два на одну таблицу
    sender    = db.relationship('User', foreign_keys=[sender_id],
                                backref=db.backref('sent_messages', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id],
                                backref=db.backref('received_messages', lazy='dynamic'))

    def __repr__(self):
        return f'<Message {self.id} from={self.sender_id} to={self.recipient_id}>'
