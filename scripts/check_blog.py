#!/usr/bin/env python3
"""Проверка сайта перед PR и в GitHub Actions. Код возврата 1 — есть ошибки.

    python3 scripts/check_blog.py            # статические проверки (без браузера)
    python3 scripts/check_blog.py --render   # + отрисовка всех страниц на 1440 и 390 px (Playwright):
                                             #   ответ 200, нет горизонтальной прокрутки, нет ошибок JS

Статические проверки:
  - JSON-LD парсится; у статей блога есть TechArticle (headline = H1, даты ГГГГ-ММ-ДД, dateModified ≥ datePublished)
    и FAQPage, вопросы которого дословно совпадают с видимыми <summary>;
  - внутренние ссылки, src и og:image ведут на существующие файлы;
  - canonical и og:url = адрес страницы; og:image статьи = /assets/og/<slug>.png и файл есть;
  - title ≤ 60, description ≤ 155 у статей; нет meta noindex (кроме 404);
  - каждая <table> внутри <div class="tbl">;
  - sitemap: все страницы есть, нет дублей и лишних адресов, lastmod — дата не позже сегодняшней;
  - у каждой статьи есть карточка в blog/index.html с data-tags (1–2 из списка), карточки по убыванию даты;
    плашка рубрики (карточка и статья) = название первой рубрики из data-tags, как на кнопках фильтра блога;
    на главной 3 карточки «Свежих статей» и это 3 самые новые статьи;
  - служебные файлы (CLAUDE.md, content-plan.csv, factcheck/, scripts/, .claude/, .github/) не попадают в dist
    (проверяется по правилам scripts/build_dist.py).
"""
import glob, html, json, os, re, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://gmt-engineering.ru'
LABELS = {'razrabotka': 'Разработка и испытания', 'po': 'Прошивки и ПО', 'sert': 'Сертификация и метрология',
          'lokal': 'Локализация и госзакупки', 'eaes': 'ЕАЭС и экспорт', 'otrasli': 'Отрасли', 'trendy': 'Тренды'}
TAGS = set(LABELS)
errors = []


def err(msg):
    errors.append(msg)


def rel(f):
    return os.path.relpath(f, REPO)


def page_url(f):
    d = os.path.relpath(os.path.dirname(f), REPO)
    return SITE + '/' if d == '.' else f'{SITE}/{d}/'


def exists(path):
    p = path.lstrip('/')
    p = os.path.join(REPO, p + 'index.html' if (p == '' or p.endswith('/')) else p)
    return os.path.exists(p)


pages = sorted(f for f in glob.glob(REPO + '/**/index.html', recursive=True)
               if not re.search(r'/(\.|node_modules|dist/|scripts/)', rel(f)))
articles = sorted(f for f in glob.glob(REPO + '/blog/*/index.html'))
today = datetime.date.today().isoformat()
art_dates = {}

for f in pages:
    t = open(f, encoding='utf-8').read()
    r = rel(f)
    url = page_url(f)
    for h in set(re.findall(r'(?:href|content|src)="(?:https://gmt-engineering\.ru)?(/[^"#?]*)"', t)):
        if not exists(h):
            err(f'{r}: битая ссылка {h}')
    if 'noindex' in t:
        err(f'{r}: meta noindex')
    m = re.search(r'<link rel="canonical" href="([^"]+)">', t)
    if not m or m[1] != url:
        err(f'{r}: canonical {m and m[1]} ≠ {url}')
    m = re.search(r'<meta property="og:url" content="([^"]+)">', t)
    if m and m[1] != url:
        err(f'{r}: og:url {m[1]} ≠ {url}')
    stripped = re.sub(r'<div class="tbl">\s*<table', '', t)
    if '<table' in stripped:
        err(f'{r}: <table> без обёртки <div class="tbl">')
    graphs = []
    for j in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', t, re.S):
        try:
            d = json.loads(j)
        except json.JSONDecodeError as e:
            err(f'{r}: JSON-LD не парсится: {e}')
            continue
        graphs += d.get('@graph', [d])
    vis_q = [html.unescape(re.sub('<[^>]+>', '', q)).strip() for q in re.findall(r'<summary>(.*?)</summary>', t, re.S)]
    for it in graphs:
        if it.get('@type') == 'FAQPage':
            if [q['name'] for q in it['mainEntity']] != vis_q:
                err(f'{r}: вопросы FAQPage в JSON-LD не совпадают с видимым FAQ')
    if f in articles:
        slug = f.split('/')[-2]
        h1 = html.unescape(re.search(r'<h1>(.*?)</h1>', t).group(1))
        ta = [g for g in graphs if g.get('@type') == 'TechArticle']
        if not ta:
            err(f'{r}: нет TechArticle в JSON-LD')
        else:
            a = ta[0]
            if a.get('headline') != h1:
                err(f'{r}: headline ≠ H1')
            dp, dm = a.get('datePublished', ''), a.get('dateModified', '')
            if not (re.fullmatch(r'\d{4}-\d{2}-\d{2}', dp) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', dm)) or dm < dp:
                err(f'{r}: даты TechArticle {dp} / {dm}')
            art_dates[slug] = dp
        if not any(g.get('@type') == 'FAQPage' for g in graphs):
            err(f'{r}: нет FAQPage в JSON-LD')
        title = html.unescape(re.search(r'<title>(.*?)</title>', t).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', t).group(1))
        if len(title) > 60:
            err(f'{r}: title {len(title)} > 60')
        if len(desc) > 155:
            err(f'{r}: description {len(desc)} > 155')
        og = re.search(r'<meta property="og:image" content="([^"]+)">', t)
        if not og or og[1] != f'{SITE}/assets/og/{slug}.png':
            err(f'{r}: og:image должен быть {SITE}/assets/og/{slug}.png')
        if not os.path.exists(f'{REPO}/assets/og/{slug}.png'):
            err(f'{r}: нет обложки assets/og/{slug}.png (scripts/og_cover.py)')

# sitemap
sm = open(REPO + '/sitemap.xml', encoding='utf-8').read()
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
if len(locs) != len(set(locs)):
    err('sitemap.xml: дубли адресов')
want = {page_url(f) for f in pages}
for u in sorted(want - set(locs)):
    err(f'sitemap.xml: нет {u}')
for u in sorted(set(locs) - want):
    err(f'sitemap.xml: лишний адрес {u}')
for loc, lm in re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', sm):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', lm) or lm > today:
        err(f'sitemap.xml: lastmod {lm} у {loc}')

# карточки блога
b = open(REPO + '/blog/index.html', encoding='utf-8').read()
cards = re.findall(r'<a class="post" href="/blog/([^/"]+)/" data-tags="([^"]*)">', b)
for slug, tags, rub in re.findall(r'<a class="post" href="/blog/([^/"]+)/" data-tags="([^"]*)"><span class="rub">([^<]*)</span>', b):
    if tags.split() and LABELS.get(tags.split()[0]) != rub:
        err(f'blog/index.html: у {slug} плашка «{rub}», а для рубрики {tags.split()[0]} нужна «{LABELS.get(tags.split()[0])}»')
    pf = f'{REPO}/blog/{slug}/index.html'
    if os.path.exists(pf):
        m = re.search(r'<div class="meta"><span>([^<]*)</span>', open(pf, encoding='utf-8').read())
        if m and m[1] != rub:
            err(f'blog/{slug}: рубрика в плашке статьи «{m[1]}» ≠ карточке «{rub}»')
seen = [c[0] for c in cards]
for slug in art_dates:
    if slug not in seen:
        err(f'blog/index.html: нет карточки статьи {slug}')
for slug, tags in cards:
    tg = tags.split()
    if not 1 <= len(tg) <= 2 or not set(tg) <= TAGS:
        err(f'blog/index.html: data-tags «{tags}» у {slug}')
order = [art_dates[s] for s in seen if s in art_dates]
if order != sorted(order, reverse=True):
    err('blog/index.html: карточки не по убыванию даты публикации')
home = open(REPO + '/index.html', encoding='utf-8').read()
lp = re.findall(r'<a class="lpost" href="/blog/([^/"]+)/"', home)
newest = sorted(art_dates, key=lambda s: art_dates[s], reverse=True)[:3]
if len(lp) != 3:
    err(f'index.html: в «Свежих статьях» {len(lp)} карточек вместо 3')
elif sorted(art_dates[s] for s in lp if s in art_dates) != sorted(art_dates[s] for s in newest):
    err(f'index.html: в «Свежих статьях» не самые новые статьи (сейчас {lp}, нужно {newest})')

# служебные файлы не должны попасть на сайт
sys.path.insert(0, os.path.join(REPO, 'scripts'))
try:
    from build_dist import skip
    for p in ['CLAUDE.md', 'content-plan.csv', 'factcheck', 'scripts', '.claude', '.github', '.gitignore']:
        if os.path.exists(os.path.join(REPO, p)) and not skip(p):
            err(f'build_dist: служебное «{p}» попадёт на сайт')
except ImportError:
    err('нет scripts/build_dist.py')

# отрисовка
if '--render' in sys.argv:
    import threading, functools, http.server
    from playwright.sync_api import sync_playwright
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=REPO)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    only = [a for a in sys.argv[1:] if a.startswith('/')]
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for vp in [{'width': 1440, 'height': 900}, {'width': 390, 'height': 844}]:
            pg = br.new_page(viewport=vp)
            js = []
            pg.on('pageerror', lambda e: js.append(str(e)))
            for f in pages:
                u = page_url(f)[len(SITE):]
                if only and u not in only:
                    continue
                resp = pg.goto(f'http://127.0.0.1:{port}{u}')
                pg.wait_for_timeout(80)
                w = pg.evaluate('document.documentElement.scrollWidth')
                if resp.status != 200:
                    err(f'{u}: ответ {resp.status}')
                if w > vp['width']:
                    err(f'{u}: горизонтальная прокрутка на {vp["width"]} px (ширина {w})')
            for e in set(js):
                err(f'ошибка JS на {vp["width"]} px: {e}')
        br.close()
    srv.shutdown()

for e in errors:
    print('ОШИБКА:', e)
print(f'check_blog: страниц {len(pages)}, статей {len(articles)}, ошибок {len(errors)}')
sys.exit(1 if errors else 0)
