from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import groupchat
from ..extensions import db
from ..models.groupchat import GroupChat, GroupChatMember, GroupChatMessage
from ..models import User


@groupchat.route('/chats')
@login_required
def list_view():
    # Чаты, в которых состоит пользователь
    memberships = GroupChatMember.query.filter_by(user_id=current_user.id).all()
    my_chat_ids = [m.chat_id for m in memberships]
    my_chats = GroupChat.query.filter(GroupChat.id.in_(my_chat_ids)).order_by(GroupChat.created_at.desc()).all()
    # Все публичные чаты (чтобы можно было вступить)
    all_chats = GroupChat.query.order_by(GroupChat.created_at.desc()).all()
    return render_template('groupchat/list.html',
                           my_chats=my_chats,
                           my_chat_ids=my_chat_ids,
                           all_chats=all_chats)


@groupchat.route('/chats/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Введите название чата.', 'warning')
        else:
            chat = GroupChat(name=name, description=description, creator_id=current_user.id)
            db.session.add(chat)
            db.session.flush()  # чтобы получить chat.id
            # Автоматически добавляем создателя как администратора
            member = GroupChatMember(chat_id=chat.id, user_id=current_user.id, is_admin=True)
            db.session.add(member)
            db.session.commit()
            flash('Чат создан!', 'success')
            return redirect(url_for('groupchat.view', chat_id=chat.id))
    return render_template('groupchat/create.html')


@groupchat.route('/chats/<int:chat_id>')
@login_required
def view(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    membership = GroupChatMember.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not membership:
        flash('Вы не состоите в этом чате. Сначала вступите.', 'warning')
        return redirect(url_for('groupchat.list_view'))
    messages = GroupChatMessage.query\
        .filter_by(chat_id=chat_id)\
        .order_by(GroupChatMessage.created_at.asc())\
        .all()
    members = GroupChatMember.query.filter_by(chat_id=chat_id).all()
    return render_template('groupchat/view.html',
                           chat=chat,
                           messages=messages,
                           members=members,
                           membership=membership)


@groupchat.route('/chats/<int:chat_id>/send', methods=['POST'])
@login_required
def send(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    membership = GroupChatMember.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not membership:
        abort(403)
    text = request.form.get('text', '').strip()
    if text:
        msg = GroupChatMessage(chat_id=chat_id, sender_id=current_user.id, text=text)
        db.session.add(msg)
        db.session.commit()
    return redirect(url_for('groupchat.view', chat_id=chat_id) + '#bottom')


@groupchat.route('/chats/<int:chat_id>/join', methods=['POST'])
@login_required
def join(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    existing = GroupChatMember.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not existing:
        member = GroupChatMember(chat_id=chat_id, user_id=current_user.id, is_admin=False)
        db.session.add(member)
        db.session.commit()
        flash(f'Вы вступили в чат «{chat.name}»!', 'success')
    return redirect(url_for('groupchat.view', chat_id=chat_id))


@groupchat.route('/chats/<int:chat_id>/leave', methods=['POST'])
@login_required
def leave(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    membership = GroupChatMember.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash(f'Вы покинули чат «{chat.name}».', 'info')
    return redirect(url_for('groupchat.list_view'))


@groupchat.route('/chats/<int:chat_id>/add_member', methods=['POST'])
@login_required
def add_member(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    membership = GroupChatMember.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not membership or not membership.is_admin:
        abort(403)
    username = request.form.get('username', '').strip()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Пользователь не найден.', 'danger')
    elif GroupChatMember.query.filter_by(chat_id=chat_id, user_id=user.id).first():
        flash('Этот пользователь уже в чате.', 'warning')
    else:
        new_member = GroupChatMember(chat_id=chat_id, user_id=user.id)
        db.session.add(new_member)
        db.session.commit()
        flash(f'{user.username} добавлен в чат.', 'success')
    return redirect(url_for('groupchat.view', chat_id=chat_id))


@groupchat.route('/chats/<int:chat_id>/delete', methods=['POST'])
@login_required
def delete(chat_id):
    chat = GroupChat.query.get_or_404(chat_id)
    if chat.creator_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(chat)
    db.session.commit()
    flash('Чат удалён.', 'info')
    return redirect(url_for('groupchat.list_view'))
