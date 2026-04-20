from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(max=256)])
    content = TextAreaField('content', validators=[DataRequired(), Length(max=5000)])
    post_type = SelectField('post_type', choices=[
        ('question', 'question'),
        ('tip',      'tip'),
    ])
    submit = SubmitField('publish')


class CommentForm(FlaskForm):
    text = TextAreaField('text', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('send')
