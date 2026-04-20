import os
import uuid
from flask import render_template, redirect, url_for, flash, current_app, abort, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import profile
from .forms import EditProfileForm
from ..extensions import db
from ..models import User


@profile.route('/profile')
@login_required
def my_profile():
    """Личный кабинет текущего пользователя."""
    from sqlalchemy import func
    from ..models.photo import Photo
    from ..models.comment import Comment

    # Считаем статистику в Python, а не в Jinja2 — избегаем проблем SQLAlchemy 2.x
    photos_count = Photo.query.filter_by(
        user_id=current_user.id, is_public=True, is_hidden=False
    ).count()

    total_likes = db.session.query(func.sum(Photo.likes_count))\
                            .filter(Photo.user_id == current_user.id)\
                            .scalar() or 0

    comments_count = Comment.query.filter_by(user_id=current_user.id).count()

    # Последние 6 фото для превью
    user_photos = Photo.query\
        .filter_by(user_id=current_user.id, is_public=True, is_hidden=False)\
        .order_by(Photo.created_at.desc())\
        .limit(6).all()

    friends_count    = current_user.get_friends_count()
    pending_in_count = current_user.get_pending_in_count()

    return render_template(
        'profile/profile.html',
        user=current_user,
        photos_count=photos_count,
        total_likes=total_likes,
        comments_count=comments_count,
        user_photos=user_photos,
        friends_count=friends_count,
        pending_in_count=pending_in_count,
    )


@profile.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Редактирование профиля."""
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.bio        = form.bio.data or ''
        current_user.telescopes = form.telescopes.data or ''
        current_user.location   = form.location.data or ''
        current_user.website    = form.website.data or ''
        current_user.twitter    = form.twitter.data or ''
        current_user.instagram  = form.instagram.data or ''

        if form.avatar.data:
            avatar_file = form.avatar.data
            ext = avatar_file.filename.rsplit('.', 1)[-1].lower()
            new_filename = f'avatar_{uuid.uuid4().hex}.{ext}'
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
            avatar_file.save(save_path)

            if current_user.avatar_filename:
                old_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    current_user.avatar_filename
                )
                if os.path.exists(old_path):
                    os.remove(old_path)

            current_user.avatar_filename = new_filename

        db.session.commit()
        flash(_('flash_profile_saved'), 'success')
        return redirect(url_for('profile.my_profile'))

    return render_template('profile/edit.html', form=form)


@profile.route('/user/<username>')
def public_profile(username):
    """Публичный профиль пользователя."""
    user = User.query.filter_by(username=username).first_or_404()
    from ..models.photo import Photo
    from sqlalchemy import func

    photos = Photo.query\
        .filter_by(user_id=user.id, is_public=True, is_hidden=False)\
        .order_by(Photo.created_at.desc())\
        .limit(12).all()

    photos_count = Photo.query.filter_by(
        user_id=user.id, is_public=True, is_hidden=False
    ).count()

    total_likes = db.session.query(func.sum(Photo.likes_count))\
                            .filter(Photo.user_id == user.id)\
                            .scalar() or 0

    friends_count = user.get_friends_count()

    # Статус дружбы текущего пользователя с этим профилем
    friendship_status = 'none'
    friendship_id = None
    if current_user.is_authenticated and current_user.id != user.id:
        friendship_status = current_user.friendship_status(user)
        from ..models.friendship import Friendship
        f = Friendship.between(current_user.id, user.id)
        if f:
            friendship_id = f.id

    return render_template(
        'profile/public.html',
        user=user,
        photos=photos,
        photos_count=photos_count,
        total_likes=total_likes,
        friends_count=friends_count,
        friendship_status=friendship_status,
        friendship_id=friendship_id,
    )


# ===================== ДРУЗЬЯ =====================

@profile.route('/friends')
@login_required
def friends_list():
    friends    = current_user.get_friends()
    pending_in = current_user.get_pending_in()
    return render_template('profile/friends.html',
                           friends=friends,
                           pending_in=pending_in)


@profile.route('/friend/request/<username>', methods=['POST'])
@login_required
def send_friend_request(username):
    target = User.query.filter_by(username=username).first_or_404()
    if target.id == current_user.id:
        flash(_('friend_self'), 'warning')
        return redirect(url_for('profile.public_profile', username=username))

    from ..models.friendship import Friendship
    existing = Friendship.between(current_user.id, target.id)
    if existing:
        flash(_('friend_already'), 'info')
        return redirect(url_for('profile.public_profile', username=username))

    f = Friendship(requester_id=current_user.id,
                   addressee_id=target.id,
                   status='pending')
    db.session.add(f)
    db.session.commit()
    flash(_('friend_request_sent'), 'success')
    return redirect(url_for('profile.public_profile', username=username))


@profile.route('/friend/accept/<int:fid>', methods=['POST'])
@login_required
def accept_friend(fid):
    from ..models.friendship import Friendship
    f = Friendship.query.get_or_404(fid)
    if f.addressee_id != current_user.id:
        abort(403)
    f.status = 'accepted'
    db.session.commit()
    flash(_('friend_request_accepted'), 'success')
    next_url = request.referrer or url_for('profile.friends_list')
    return redirect(next_url)


@profile.route('/friend/decline/<int:fid>', methods=['POST'])
@login_required
def decline_friend(fid):
    from ..models.friendship import Friendship
    f = Friendship.query.get_or_404(fid)
    if f.addressee_id != current_user.id:
        abort(403)
    db.session.delete(f)
    db.session.commit()
    flash(_('friend_request_declined'), 'info')
    next_url = request.referrer or url_for('profile.friends_list')
    return redirect(next_url)


@profile.route('/friend/remove/<username>', methods=['POST'])
@login_required
def remove_friend(username):
    target = User.query.filter_by(username=username).first_or_404()
    from ..models.friendship import Friendship
    f = Friendship.between(current_user.id, target.id)
    if f and f.status == 'accepted':
        db.session.delete(f)
        db.session.commit()
        flash(_('friend_removed'), 'info')
    return redirect(url_for('profile.public_profile', username=username))
