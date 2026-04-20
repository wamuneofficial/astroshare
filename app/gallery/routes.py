from flask import render_template, request
from . import gallery
from ..extensions import db
from ..models import Photo
from ..photos.forms import OBJECT_TYPE_CHOICES


@gallery.route('/gallery')
def gallery_view():
    page        = request.args.get('page', 1, type=int)
    object_type = request.args.get('type', '')
    sort        = request.args.get('sort', 'new')

    query = Photo.query.filter_by(is_public=True, is_hidden=False)

    if object_type:
        query = query.filter_by(object_type=object_type)

    if sort == 'popular':
        query = query.order_by(Photo.likes_count.desc(), Photo.created_at.desc())
    else:
        query = query.order_by(Photo.created_at.desc())

    pagination = db.paginate(query, per_page=20, error_out=False)

    # Убираем пустой первый элемент из списка типов для фильтра
    type_choices = [(v, l) for v, l in OBJECT_TYPE_CHOICES if v]

    return render_template('gallery/gallery.html',
                           pagination=pagination,
                           current_type=object_type,
                           current_sort=sort,
                           type_choices=type_choices)
