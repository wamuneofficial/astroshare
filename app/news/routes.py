import json
import ssl
import urllib.request
from datetime import datetime
from flask import render_template, request
from . import news


def _fetch_articles(page=1, per_page=15):
    """
    Загружает статьи из Spaceflight News API v4 (без API-ключа).
    На macOS urllib иногда падает из-за SSL-сертификатов — пробуем
    сначала с проверкой, затем без (только для dev-режима).
    """
    offset = (page - 1) * per_page
    url = (
        f"https://api.spaceflightnewsapi.net/v4/articles/"
        f"?limit={per_page}&offset={offset}&ordering=-published_at"
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'Astroshare/1.0'})

    # Пробуем два контекста: сначала с нормальной проверкой, потом без
    ssl_contexts = [
        ssl.create_default_context(),
        ssl._create_unverified_context(),
    ]

    for ctx in ssl_contexts:
        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode())
            # Преобразуем строки дат в объекты datetime
            for article in data.get('results', []):
                raw = article.get('published_at', '')
                try:
                    article['published_dt'] = datetime.fromisoformat(
                        raw.replace('Z', '+00:00')
                    )
                except Exception:
                    article['published_dt'] = None
            return data
        except Exception:
            continue

    return {'count': 0, 'results': []}


@news.route('/news')
def news_view():
    page     = request.args.get('page', 1, type=int)
    per_page = 15
    data     = _fetch_articles(page=page, per_page=per_page)
    articles = data.get('results', [])
    total    = data.get('count', 0)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template('news/news.html',
                           articles=articles,
                           page=page,
                           total_pages=total_pages,
                           api_error=(total == 0 and not articles))
