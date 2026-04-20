import json
import urllib.request
import urllib.parse
from flask import render_template, request
from . import identify


def _simbad_search(name):
    """
    Ищет объект в базе SIMBAD (Centre de Données astronomiques de Strasbourg)
    по имени или каталожному обозначению (M31, NGC 1952, Alpha Cen...).
    Возвращает словарь с полями или None.
    """
    # Защита от SQL-инъекций в ADQL: удваиваем одинарные кавычки
    safe = name.replace("'", "''")

    adql = (
        "SELECT TOP 1 basic.main_id, ra, dec, otype_txt "
        "FROM basic "
        "JOIN ident ON ident.oidref = basic.oid "
        f"WHERE ident.id = '{safe}'"
    )
    params = urllib.parse.urlencode({
        'REQUEST': 'doQuery',
        'LANG':    'ADQL',
        'FORMAT':  'json',
        'QUERY':   adql,
    })
    url = f"https://simbad.cds.unistra.fr/simbad/sim-tap/sync?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Astroshare/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data.get('data'):
            cols = [c['name'] for c in data['metadata']]
            return dict(zip(cols, data['data'][0]))
    except Exception:
        pass
    return None


@identify.route('/identify')
def identify_view():
    query  = request.args.get('q', '').strip()
    result = None
    error  = None

    if query:
        result = _simbad_search(query)
        if not result:
            error = 'not_found'

    return render_template('identify/identify.html',
                           query=query,
                           result=result,
                           error=error)
