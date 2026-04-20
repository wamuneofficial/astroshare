import os
from flask import render_template, session, redirect, url_for, request, current_app, send_from_directory
from . import main


@main.route('/')
def index():
    """Главная страница — лента снимков и постов."""
    from ..models import Photo, Post
    page     = request.args.get('page', 1, type=int)
    per_page = 12

    all_photos = Photo.query.filter_by(is_public=True, is_hidden=False).all()
    all_posts  = Post.query.filter_by(is_hidden=False).all()

    feed = sorted(
        [{'kind': 'photo', 'item': p, 'date': p.created_at} for p in all_photos] +
        [{'kind': 'post',  'item': p, 'date': p.created_at} for p in all_posts],
        key=lambda x: x['date'],
        reverse=True
    )

    total       = len(feed)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = min(page, total_pages)
    page_items  = feed[(page - 1) * per_page : page * per_page]

    return render_template('index.html',
                           feed_items=page_items,
                           page=page,
                           total_pages=total_pages)


@main.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Отдаёт загруженные пользователями файлы.
    send_from_directory автоматически защищает от path traversal атак.
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main.route('/set-language/<lang>')
def set_language(lang):
    """
    Переключение языка интерфейса.
    Сохраняем выбранный язык в сессии и возвращаем
    пользователя на страницу, с которой он пришёл.
    """
    if lang in ['ru', 'en']:
        session['lang'] = lang
        # permanent=True — сессия сохраняется даже после закрытия браузера
        session.permanent = True

    # request.referrer — адрес страницы, с которой пришёл запрос.
    # Если referrer нет (например, пользователь открыл ссылку напрямую) — идём на главную.
    return redirect(request.referrer or url_for('main.index'))
