import os
import uuid
from flask import render_template, redirect, url_for, flash, request, abort, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import materials
from ..extensions import db
from ..models.material import Material

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'xlsx', 'xls'}
MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 МБ


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def can_edit():
    return current_user.is_authenticated and (
        current_user.is_admin or getattr(current_user, 'can_edit_materials', False)
    )


def _save_file(file_obj):
    """Сохраняет файл в uploads/, возвращает (stored_name, original_name, size)."""
    original = secure_filename(file_obj.filename)
    ext = original.rsplit('.', 1)[1].lower() if '.' in original else ''
    stored = f"mat_{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], stored)
    file_obj.save(dest)
    size = os.path.getsize(dest)
    return stored, original, size


def _delete_file(stored_name):
    if stored_name:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
        if os.path.isfile(path):
            os.remove(path)


@materials.route('/materials')
def list_view():
    items = Material.query.order_by(Material.created_at.desc()).all()
    return render_template('materials/list.html', items=items, can_edit=can_edit())


@materials.route('/materials/<int:material_id>')
def view(material_id):
    item = Material.query.get_or_404(material_id)
    return render_template('materials/view.html', item=item, can_edit=can_edit())


@materials.route('/materials/file/<int:material_id>')
def download_file(material_id):
    """Скачивание прикреплённого файла."""
    item = Material.query.get_or_404(material_id)
    if not item.file_path:
        abort(404)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        item.file_path,
        as_attachment=True,
        download_name=item.file_original_name or item.file_path,
    )


@materials.route('/materials/new', methods=['GET', 'POST'])
@login_required
def new():
    if not can_edit():
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('Введите заголовок.', 'warning')
            return render_template('materials/edit.html', item=None)

        item = Material(title=title, content=content, author_id=current_user.id)

        file = request.files.get('attachment')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Недопустимый тип файла.', 'danger')
                return render_template('materials/edit.html', item=None)
            stored, original, size = _save_file(file)
            item.file_path = stored
            item.file_original_name = original
            item.file_size = size

        db.session.add(item)
        db.session.commit()
        flash('Материал добавлен.', 'success')
        return redirect(url_for('materials.view', material_id=item.id))

    return render_template('materials/edit.html', item=None)


@materials.route('/materials/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(material_id):
    if not can_edit():
        abort(403)
    item = Material.query.get_or_404(material_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('Введите заголовок.', 'warning')
            return render_template('materials/edit.html', item=item)

        item.title = title
        item.content = content

        # Замена файла
        file = request.files.get('attachment')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Недопустимый тип файла.', 'danger')
                return render_template('materials/edit.html', item=item)
            _delete_file(item.file_path)
            stored, original, size = _save_file(file)
            item.file_path = stored
            item.file_original_name = original
            item.file_size = size

        # Удаление файла
        if request.form.get('remove_file') == '1':
            _delete_file(item.file_path)
            item.file_path = ''
            item.file_original_name = ''
            item.file_size = 0

        db.session.commit()
        flash('Материал обновлён.', 'success')
        return redirect(url_for('materials.view', material_id=item.id))

    return render_template('materials/edit.html', item=item)


@materials.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
def delete(material_id):
    if not can_edit():
        abort(403)
    item = Material.query.get_or_404(material_id)
    _delete_file(item.file_path)
    db.session.delete(item)
    db.session.commit()
    flash('Материал удалён.', 'info')
    return redirect(url_for('materials.list_view'))
