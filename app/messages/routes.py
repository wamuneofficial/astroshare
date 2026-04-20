from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import messages
from .forms import ComposeForm, ReplyForm
from ..extensions import db
from ..models import User
from ..models.message import Message


@messages.route('/messages')
@login_required
def inbox():
    """Входящие сообщения."""
    page     = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Message.query\
        .filter_by(recipient_id=current_user.id)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('messages/inbox.html',
                           pagination=pagination,
                           tab='inbox')


@messages.route('/messages/sent')
@login_required
def sent():
    """Отправленные сообщения."""
    page     = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Message.query\
        .filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('messages/inbox.html',
                           pagination=pagination,
                           tab='sent')


@messages.route('/messages/compose', methods=['GET', 'POST'])
@messages.route('/messages/compose/<username>', methods=['GET', 'POST'])
@login_required
def compose(username=None):
    """Написать новое сообщение."""
    form = ComposeForm()
    # Если username передан через URL — подставляем в поле получателя
    if username and request.method == 'GET':
        form.recipient.data = username

    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if recipient is None:
            flash(_('msg_user_not_found'), 'danger')
        elif recipient.id == current_user.id:
            flash(_('msg_self_send'), 'warning')
        else:
            msg = Message(
                sender_id=current_user.id,
                recipient_id=recipient.id,
                subject=form.subject.data,
                body=form.body.data,
            )
            db.session.add(msg)
            db.session.commit()
            flash(_('msg_sent'), 'success')
            return redirect(url_for('messages.sent'))

    return render_template('messages/compose.html', form=form)


@messages.route('/messages/<int:message_id>')
@login_required
def view_message(message_id):
    """Просмотр отдельного сообщения."""
    msg = Message.query.get_or_404(message_id)
    # Сообщение видит только отправитель или получатель
    if msg.sender_id != current_user.id and msg.recipient_id != current_user.id:
        abort(403)
    # Помечаем как прочитанное
    if msg.recipient_id == current_user.id and not msg.is_read:
        msg.is_read = True
        db.session.commit()

    reply_form = ReplyForm()
    return render_template('messages/view.html', msg=msg, reply_form=reply_form)


@messages.route('/messages/<int:message_id>/reply', methods=['POST'])
@login_required
def reply(message_id):
    """Ответить на сообщение."""
    original = Message.query.get_or_404(message_id)
    if original.sender_id != current_user.id and original.recipient_id != current_user.id:
        abort(403)

    form = ReplyForm()
    if form.validate_on_submit():
        # Определяем получателя ответа
        to_id = (original.sender_id
                 if original.recipient_id == current_user.id
                 else original.recipient_id)
        reply_msg = Message(
            sender_id=current_user.id,
            recipient_id=to_id,
            subject='Re: ' + original.subject,
            body=form.body.data,
        )
        db.session.add(reply_msg)
        db.session.commit()
        flash(_('msg_sent'), 'success')
    return redirect(url_for('messages.inbox'))


@messages.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Удалить сообщение."""
    msg = Message.query.get_or_404(message_id)
    if msg.sender_id != current_user.id and msg.recipient_id != current_user.id:
        abort(403)
    db.session.delete(msg)
    db.session.commit()
    flash(_('msg_deleted'), 'info')
    return redirect(url_for('messages.inbox'))
