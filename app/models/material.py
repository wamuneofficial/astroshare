from datetime import datetime
from ..extensions import db


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Прикреплённый файл (PDF, DOCX, изображение и др.)
    file_path = db.Column(db.String(256), default='')          # имя файла в uploads/
    file_original_name = db.Column(db.String(256), default='') # оригинальное имя для скачивания
    file_size = db.Column(db.Integer, default=0)               # размер в байтах

    author = db.relationship('User', backref=db.backref('materials', lazy='dynamic'))
