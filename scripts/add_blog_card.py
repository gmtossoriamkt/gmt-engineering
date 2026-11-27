#!/usr/bin/env python3
"""Встраивает новую статью в сайт: карточка первой в blog/index.html, карточка первой в «Свежих статьях»
на главной (третья убирается), запись в sitemap.xml и lastmod у /blog/ и главной.
Данные берутся со страницы статьи (H1, рубрика, дата, время чтения, og:description).

Использование:
    python3 scripts/add_blog_card.py <slug> --tags "sert" --home-title "Короткий H1 для главной" --home-desc "Одна строка" [--dry-run]

Рубрики (data-tags, 1–2 через пробел): razrabotka, po, sert, lokal, eaes, otrasli, trendy.
"""
import re, sys, os, html, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS = {'razrabotka', 'po', 'sert', 'lokal', 'eaes', 'otrasli', 'trendy'}
MONTHS = 'января февраля марта апреля мая июня июля августа сентября октября ноября декабря'.split()


def read(p):
    return open(os.path.join(REPO, p), encoding='utf-8').read()


def write(p, s, dry):
    if not dry:
        open(os.path.join(REPO, p), 'w', encoding='utf-8').write(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--tags', required=True)
    ap.add_argument('--home-title', required=True)
    ap.add_argument('--home-desc', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    tags = a.tags.split()
    if not 1 <= len(tags) <= 2 or not set(tags) <= TAGS:
        sys.exit(f'add_blog_card: --tags — 1–2 значения из {sorted(TAGS)}')
    page = read(f'blog/{a.slug}/index.html')
    h1 = re.search(r'<h1>(.*?)</h1>', page).group(1)
    meta = re.findall(r'<span>(.*?)</span>', re.search(r'<div class="meta">(.*?)</div>', page).group(1))
    rubric, date_ru, read_min = meta[0], meta[1], re.match(r'\d+', meta[2]).group(0)
    card = re.search(r'<meta property="og:description" content="(.*?)">', page).group(1)
    date = re.search(r'"datePublished": "(\d{4}-\d{2}-\d{2})"', page).group(1)
    url = f'/blog/{a.slug}/'

    # 1. Блог
    s = read('blog/index.html')
    if f'href="{url}"' in s:
        sys.exit('add_blog_card: карточка уже есть в blog/index.html')
    line = (f'    <a class="post" href="{url}" data-tags="{" ".join(tags)}"><span class="rub">{rubric}</span>'
            f'<h2>{h1}</h2><p>{card}</p><span class="foot"><span>{date_ru} · {read_min} мин</span><b>Читать →</b></span></a>\n')
    i = s.index('    <a class="post"')
    write('blog/index.html', s[:i] + line + s[i:], a.dry_run)

    # 2. Главная: «Свежие статьи»
    s = read('index.html')
    lp = re.findall(r'      <a class="lpost".*?</a>\n', s)
    if len(lp) != 3:
        sys.exit(f'add_blog_card: на главной ожидалось 3 карточки .lpost, найдено {len(lp)}')
    new = (f'      <a class="lpost" href="{url}"><span class="rub">{rubric}</span><h3>{html.escape(a.home_title, quote=False)}</h3>'
           f'<p>{html.escape(a.home_desc, quote=False)}</p><span class="foot"><span>{date_ru}</span><b>Читать →</b></span></a>\n')
    s = s.replace(lp[2], '', 1).replace(lp[0], new + lp[0], 1)
    write('index.html', s, a.dry_run)

    # 3. sitemap.xml
    s = read('sitemap.xml')
    loc = f'https://gmt-engineering.ru{url}'
    if loc in s:
        sys.exit('add_blog_card: адрес уже есть в sitemap.xml')
    s, n = re.subn(r'(<url><loc>https://gmt-engineering\.ru/blog/</loc><lastmod>)[^<]+(</lastmod></url>\n)',
                   lambda m: m[1] + date + m[2] + f'  <url><loc>{loc}</loc><lastmod>{date}</lastmod></url>\n', s, count=1)
    if n != 1:
        sys.exit('add_blog_card: в sitemap.xml не найдена запись /blog/')
    s = re.sub(r'(<url><loc>https://gmt-engineering\.ru/</loc><lastmod>)[^<]+', lambda m: m[1] + date, s, count=1)
    write('sitemap.xml', s, a.dry_run)
    print(('[dry-run] ' if a.dry_run else '') + f'{url}: карточка в блоге и на главной, sitemap ({date})')


if __name__ == '__main__':
    main()
