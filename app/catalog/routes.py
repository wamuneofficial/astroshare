from flask import render_template, request, abort
from . import catalog
from .data import CATALOG, CATALOG_BY_ID, OBJECT_TYPES

# Переводы типов объектов для русского интерфейса
TYPE_LABELS_RU = {
    'solar':        'Солнечная система',
    'star':         'Звёзды',
    'nebula':       'Туманности',
    'star_cluster': 'Звёздные скопления',
    'galaxy':       'Галактики',
}
TYPE_LABELS_EN = {
    'solar':        'Solar System',
    'star':         'Stars',
    'nebula':       'Nebulae',
    'star_cluster': 'Star Clusters',
    'galaxy':       'Galaxies',
}


@catalog.route('/catalog')
def catalog_view():
    """Каталог космических объектов с поиском и фильтрацией."""
    query    = request.args.get('q', '').strip().lower()
    type_f   = request.args.get('type', '')
    sort_by  = request.args.get('sort', 'name')

    items = list(CATALOG)

    # Фильтр по типу объекта
    if type_f and type_f in OBJECT_TYPES:
        items = [o for o in items if o['type'] == type_f]

    # Полнотекстовый поиск по имени, рус. имени и каталожному ID
    if query:
        items = [
            o for o in items
            if query in o['name'].lower()
            or query in o['name_ru'].lower()
            or query in o['catalog_id'].lower()
            or query in o.get('constellation', '').lower()
        ]

    # Сортировка
    if sort_by == 'distance':
        items = sorted(items, key=lambda o: o['distance_ly'])
    elif sort_by == 'magnitude':
        items = sorted(
            items,
            key=lambda o: (o['magnitude'] is None, o['magnitude'] or 99)
        )
    else:
        items = sorted(items, key=lambda o: o['name_ru'])

    return render_template(
        'catalog/catalog.html',
        items=items,
        query=request.args.get('q', ''),
        type_f=type_f,
        sort_by=sort_by,
        object_types=OBJECT_TYPES,
        type_labels_ru=TYPE_LABELS_RU,
        type_labels_en=TYPE_LABELS_EN,
        total=len(items),
    )


@catalog.route('/catalog/<object_id>')
def object_detail(object_id):
    """Страница отдельного объекта каталога."""
    obj = CATALOG_BY_ID.get(object_id)
    if obj is None:
        abort(404)
    return render_template('catalog/object.html', obj=obj)
