from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import materials
from ..extensions import db
from ..models.material import Material


def can_edit():
    return current_user.is_authenticated and (
        current_user.is_admin or getattr(current_user, 'can_edit_materials', False)
    )


@materials.route('/materials')
def list_view():
    items = Material.query.order_by(Material.created_at.desc()).all()
    return render_template('materials/list.html', items=items, can_edit=can_edit())


@materials.route('/materials/<int:material_id>')
def view(material_id):
    item = Material.query.get_or_404(material_id)
    return render_template('materials/view.html', item=item, can_edit=can_edit())


@materials.route('/materials/new', methods=['GET', 'POST'])
@login_required
def new():
    if not can_edit():
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash('Заполните все поля.', 'warning')
        else:
            item = Material(title=title, content=content, author_id=current_user.id)
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
        if not title or not content:
            flash('Заполните все поля.', 'warning')
        else:
            item.title = title
            item.content = content
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
    db.session.delete(item)
    db.session.commit()
    flash('Материал удалён.', 'info')
    return redirect(url_for('materials.list_view'))
