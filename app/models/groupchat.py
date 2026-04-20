from datetime import datetime
from ..extensions import db


class GroupChat(db.Model):
    __tablename__ = 'group_chats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), default='')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref=db.backref('created_chats', lazy='dynamic'))
    members = db.relationship('GroupChatMember', backref='chat', lazy='dynamic',
                              cascade='all, delete-orphan')
    chat_messages = db.relationship('GroupChatMessage', backref='chat', lazy='dynamic',
                                    cascade='all, delete-orphan')


class GroupChatMember(db.Model):
    __tablename__ = 'group_chat_members'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('group_chats.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('chat_memberships', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('chat_id', 'user_id', name='uq_chat_member'),
    )


class GroupChatMessage(db.Model):
    __tablename__ = 'group_chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('group_chats.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', backref=db.backref('group_messages', lazy='dynamic'))
