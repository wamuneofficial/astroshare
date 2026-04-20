from flask import render_template, redirect, url_for, flash, abort, current_app, jsonify, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import photos
from .forms import PhotoUploadForm
from ..extensions import db
from ..models import Photo, Like
from ..services.storage import storage
from ..services.image_processor import process_upload


@photos.route('/photos/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Страница загрузки нового снимка."""
    form = PhotoUploadForm()

    if form.validate_on_submit():
        # Обрабатываем файл: сохраняем и создаём превью
        result = process_upload(
            form.photo.data,
            current_app.config['UPLOAD_FOLDER']
        )

        if result['error']:
            flash(_(result['error']), 'danger')
            return redirect(url_for('photos.upload'))

        # Создаём запись в БД
        photo = Photo(
            user_id=current_user.id,
            filename=result['filename'],
            original_filename=form.photo.data.filename,
            thumbnail_filename=result['thumbnail'] or '',
            file_format=result['file_format'],

            title=form.title.data,
            description=form.description.data or '',
            observation_date=form.observation_date.data,
            is_public=form.is_public.data,

            object_name=form.object_name.data or '',
            object_type=form.object_type.data or '',
            constellation=form.constellation.data or '',
            ra=form.ra.data or '',
            dec=form.dec.data or '',

            telescope=form.telescope.data or '',
            focal_length=form.focal_length.data or None,
            camera=form.camera.data or '',
            exposure_time=form.exposure_time.data or None,
            iso_gain=form.iso_gain.data or '',
            frame_count=form.frame_count.data or None,

            location_name=form.location_name.data or '',
            # Шкала Бортля: пустая строка → None
            bortle_scale=int(form.bortle_scale.data) if form.bortle_scale.data else None,

            tags=form.tags.data or '',
        )

        db.session.add(photo)
        db.session.commit()

        flash(_('flash_photo_uploaded'), 'success')
        return redirect(url_for('photos.photo_detail', photo_id=photo.id))

    return render_template('photos/upload.html', form=form)


@photos.route('/photos/my')
@login_required
def my_photos():
    """Личная галерея пользователя — все его снимки."""
    page = db.paginate(
        db.select(Photo)
          .where(Photo.user_id == current_user.id)
          .order_by(Photo.created_at.desc()),
        per_page=16,
        error_out=False
    )
    return render_template('photos/my_photos.html', pagination=page)


@photos.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    """Страница отдельного снимка."""
    photo = Photo.query.get_or_404(photo_id)

    # Приватные снимки видит только владелец
    if not photo.is_public and (
        not current_user.is_authenticated or current_user.id != photo.user_id
    ):
        abort(403)

    # Скрытые модератором снимки недоступны никому кроме владельца и админа
    if photo.is_hidden and (
        not current_user.is_authenticated or
        (current_user.id != photo.user_id and not current_user.is_admin)
    ):
        abort(404)

    from ..models import Comment, Like
    from ..posts.forms import CommentForm

    comment_form = CommentForm()
    comments = Comment.query.filter_by(photo_id=photo_id, parent_id=None)\
                            .order_by(Comment.created_at.asc()).all()
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(
            user_id=current_user.id, photo_id=photo_id
        ).first() is not None

    return render_template('photos/photo.html',
                           photo=photo,
                           comment_form=comment_form,
                           comments=comments,
                           liked=liked)


@photos.route('/photo/<int:photo_id>/like', methods=['POST'])
@login_required
def toggle_like(photo_id):
    """AJAX-эндпоинт для постановки/снятия лайка."""
    photo = Photo.query.get_or_404(photo_id)
    existing = Like.query.filter_by(
        user_id=current_user.id, photo_id=photo_id
    ).first()

    if existing:
        db.session.delete(existing)
        photo.likes_count = max(0, photo.likes_count - 1)
        liked = False
    else:
        like = Like(user_id=current_user.id, photo_id=photo_id)
        db.session.add(like)
        photo.likes_count += 1
        liked = True

    db.session.commit()
    return jsonify({'liked': liked, 'likes_count': photo.likes_count})


@photos.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    """Добавление комментария к снимку."""
    from ..models import Comment
    from ..posts.forms import CommentForm
    photo = Photo.query.get_or_404(photo_id)
    form = CommentForm()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id', type=int)
        comment = Comment(
            photo_id=photo_id,
            user_id=current_user.id,
            text=form.text.data,
            parent_id=parent_id,
        )
        db.session.add(comment)
        db.session.commit()
        flash(_('flash_comment_added'), 'success')
    return redirect(url_for('photos.photo_detail', photo_id=photo_id))


@photos.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """Удаление снимка владельцем."""
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    # Удаляем файлы с диска
    storage.delete(photo.filename)
    if photo.thumbnail_filename:
        storage.delete(photo.thumbnail_filename)

    db.session.delete(photo)
    db.session.commit()

    flash(_('flash_photo_deleted'), 'info')
    return redirect(url_for('photos.my_photos'))
