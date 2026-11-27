#!/usr/bin/env python3
"""Собирает страницу статьи блога из конфига на основе последней опубликованной статьи
(шапка, меню, футер, стили, скрипты берутся из неё — так статья всегда на актуальном шаблоне).

Использование:
    python3 scripts/new_article.py <config.py> [--template blog/<slug>/index.html]

Конфиг — Python-файл ВНЕ репозитория со словарём A:
    slug, title (≤60), desc (≤155), card (описание для карточки и og:description),
    h1, crumb, rubric (текст плашки), date (ГГГГ-ММ-ДД), date_ru («26 ноября 2026»), read (мин),
    cta_href, toc_btn, toc [(id, пункт)], related [(название, подпись, href)],
    faq [(вопрос, ответ-html)], body (html статьи; место FAQ — строка {FAQ}).
"""
import re, json, html, sys, os, glob, importlib.util

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://gmt-engineering.ru'


def esc(s):
    return html.escape(s, quote=True)


def latest_article(exclude=None):
    best = None
    for f in glob.glob(f'{REPO}/blog/*/index.html'):
        slug = f.split('/')[-2]
        if slug == exclude:
            continue
        m = re.search(r'"datePublished": "(\d{4}-\d{2}-\d{2})"', open(f, encoding='utf-8').read())
        if m and (best is None or m[1] > best[0]):
            best = (m[1], f)
    return best[1]


def sub1(pattern, repl, text, flags=0):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        sys.exit(f'new_article: в шаблоне не найден фрагмент: {pattern[:70]}')
    return new


def build(A, tpl=None):
    tpl = tpl or latest_article(exclude=A['slug'])
    t = open(tpl, encoding='utf-8').read()
    old_slug = tpl.split('/')[-2]
    url = f"{SITE}/blog/{A['slug']}/"
    og = f"{SITE}/assets/og/{A['slug']}.png"
    t = sub1(r'<title>.*?</title>', lambda m: f"<title>{esc(A['title'])}</title>", t)
    t = sub1(r'<meta name="description" content=".*?">', lambda m: f'<meta name="description" content="{esc(A["desc"])}">', t)
    t = sub1(r'<link rel="canonical" href=".*?">', lambda m: f'<link rel="canonical" href="{url}">', t)
    t = sub1(r'<meta property="og:title" content=".*?">', lambda m: f'<meta property="og:title" content="{esc(A["h1"])}">', t)
    t = sub1(r'<meta property="og:description" content=".*?">', lambda m: f'<meta property="og:description" content="{esc(A["card"])}">', t)
    t = sub1(r'<meta property="og:url" content=".*?">', lambda m: f'<meta property="og:url" content="{url}">', t)
    t = sub1(r'<meta property="og:image" content=".*?">', lambda m: f'<meta property="og:image" content="{og}">', t)
    t = sub1(r'<meta name="twitter:image" content=".*?">', lambda m: f'<meta name="twitter:image" content="{og}">', t)
    faq_ld = [{"@type": "Question", "name": q,
               "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub('<[^>]+>', '', a))}} for q, a in A['faq']]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "TechArticle", "headline": A['h1'], "description": A['desc'],
         "datePublished": A['date'], "dateModified": A.get('date_modified', A['date']),
         "inLanguage": "ru", "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": "Инженерная команда ГМТ Инжиниринг"},
         "publisher": {"@type": "Organization", "name": "ГМТ Инжиниринг",
                       "legalName": "ООО «Глобальные Медицинские Технологии»", "url": SITE + "/"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Блог", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": A['crumb']}]},
        {"@type": "FAQPage", "mainEntity": faq_ld}]}
    t = sub1(r'(<script type="application/ld\+json">\n).*?(\n</script>)',
             lambda m: m[1] + json.dumps(ld, ensure_ascii=False) + m[2], t, flags=re.S)
    t = sub1(r'(<a href="/blog/">Блог</a><span aria-hidden="true">/</span><span>).*?(</span></nav>)',
             lambda m: m[1] + esc(A['crumb']) + m[2], t)
    t = sub1(r'<h1>.*?</h1>', lambda m: f"<h1>{esc(A['h1'])}</h1>", t)
    t = sub1(r'<div class="meta">.*?</div>', lambda m: (
        f'<div class="meta"><span>{A["rubric"]}</span><span>{A["date_ru"]}</span>'
        f'<span>{A["read"]} минут</span><span>Инженерная команда ГМТ Инжиниринг</span></div>'), t)
    faq_html = '<div class="faq">\n' + ''.join(
        f'        <details><summary>{esc(q)}</summary><p>{a}</p></details>\n' for q, a in A['faq']) + '      </div>'
    body = A['body'].replace('{FAQ}', faq_html)
    t = sub1(r'(<article class="prose">\n).*?(\n    </article>)', lambda m: m[1] + body + m[2], t, flags=re.S)
    toc = ''.join(f'        <li><a href="#{i}">{esc(n)}</a></li>\n' for i, n in A['toc'])
    t = sub1(r'(<b>Содержание</b>\n      <ol>\n).*?(      </ol>\n      <a class="btn btn-cta" href=")[^"]*(">).*?(</a>)',
             lambda m: m[1] + toc + m[2] + A['cta_href'] + m[3] + esc(A['toc_btn']) + m[4], t, flags=re.S)
    rel = ''.join(f'      <a href="{h}">{esc(n)}<span>{esc(d)}</span></a>\n' for n, d, h in A['related'])
    t = sub1(r'(<div class="rel">\n).*?(    </div>\n  </section>)', lambda m: m[1] + rel + m[2], t, flags=re.S)
    if f'/blog/{old_slug}/' in t.split('</head>')[0]:
        sys.exit(f'new_article: в <head> остались ссылки на шаблон {old_slug}')
    out = f"{REPO}/blog/{A['slug']}/index.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(t)
    txt = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', body))
    print(f"{A['slug']}: шаблон {old_slug}; title {len(A['title'])}, desc {len(A['desc'])}, текст {len(txt)} знаков")
    if len(A['title']) > 60 or len(A['desc']) > 155:
        print('ВНИМАНИЕ: title > 60 или description > 155 знаков')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec = importlib.util.spec_from_file_location('cfg', sys.argv[1])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    tpl = None
    if '--template' in sys.argv:
        tpl = os.path.join(REPO, sys.argv[sys.argv.index('--template') + 1])
    build(m.A, tpl)
