#!/usr/bin/env python3
"""Обложка статьи для превью ссылок: assets/og/<slug>.png, 1200×630, в стиле остальных обложек.
Рубрика и H1 берутся из страницы статьи.

Использование: python3 scripts/og_cover.py <slug> [<slug> ...]
Нужен Playwright (Chromium); локальный сервер поднимается сам.
"""
import re, sys, os, html, threading, functools, http.server
from playwright.sync_api import sync_playwright
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = '''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/fonts.css"><style>
*{box-sizing:border-box;margin:0}body{width:1200px;height:630px;background:#102B3F;font-family:Montserrat,sans-serif;color:#fff;position:relative;overflow:hidden}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 1.2px,transparent 1.2px);background-size:24px 24px}
.wrap{position:absolute;left:80px;top:70px;right:330px;bottom:60px;display:flex;flex-direction:column}
.logo{display:flex;align-items:center;gap:18px;font-weight:800;font-size:36px;letter-spacing:.5px}
.logo i{width:3px;height:38px;background:#00B3B3;display:block}.logo span{font-weight:600;font-size:17px;letter-spacing:6px}
.rub{margin-top:46px;align-self:flex-start;border:2px solid #00B3B3;color:#5fd6d6;border-radius:999px;padding:8px 18px;font-weight:600;font-size:19px}
h1{margin-top:22px;font-weight:700;line-height:1.12;letter-spacing:-.5px}
.foot{margin-top:auto;display:flex;align-items:center;gap:18px;font-weight:600;font-size:22px;color:#cfe3ee}.foot b{width:46px;height:3px;background:#00B3B3;display:block}
svg{position:absolute;right:40px;top:115px}
</style></head><body><div class="dots"></div>
<svg width="260" height="400" viewBox="0 0 260 400" fill="none" stroke="#5fc4c4" stroke-width="3">
<rect x="70" y="130" width="150" height="150" rx="16" fill="#163954" stroke="#7fd1d1"/><rect x="108" y="168" width="74" height="74" rx="6" stroke="#00B3B3"/>
<path d="M100 130V60H60V20"/><path d="M145 130V40"/><path d="M190 130V80H240V30"/><path d="M70 170H20V120"/><path d="M70 215H10"/><path d="M70 255H30V300"/>
<path d="M100 280V350H60V380"/><path d="M145 280V370"/><path d="M190 280V330H240"/>
<g fill="#00B3B3" stroke="none"><circle cx="60" cy="20" r="7"/><circle cx="145" cy="40" r="7"/><circle cx="240" cy="30" r="7"/><circle cx="20" cy="120" r="7"/><circle cx="10" cy="215" r="7"/><circle cx="30" cy="300" r="7"/><circle cx="60" cy="380" r="7"/><circle cx="145" cy="370" r="7"/><circle cx="240" cy="330" r="7"/></g></svg>
<div class="wrap"><div class="logo">ГМТ<i></i><span>ИНЖИНИРИНГ</span></div><div class="rub">{rub}</div><h1 id="h">{title}</h1>
<div class="foot"><b></b>Блог · gmt-engineering.ru</div></div></body></html>'''


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=REPO)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main(slugs):
    srv = serve()
    port = srv.server_address[1]
    tmp = os.path.join(REPO, '_og_tmp.html')
    os.makedirs(os.path.join(REPO, 'assets/og'), exist_ok=True)
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={'width': 1200, 'height': 630})
            for slug in slugs:
                t = open(f'{REPO}/blog/{slug}/index.html', encoding='utf-8').read()
                h1 = html.unescape(re.search(r'<h1>(.*?)</h1>', t).group(1))
                h1 = re.sub(r'(?:(?<=\s)|^)([^\s]{1,2}) ', '\\1\u00a0', h1)
                h1 = re.sub(r' (\d{4})$', '\u00a0\\1', h1)
                rub = html.unescape(re.search(r'<div class="meta"><span>(.*?)</span>', t).group(1))
                open(tmp, 'w', encoding='utf-8').write(TPL.replace('{rub}', html.escape(rub)).replace('{title}', html.escape(h1)))
                pg.goto(f'http://127.0.0.1:{port}/_og_tmp.html?{slug}')
                pg.evaluate('document.fonts.ready')
                pg.evaluate("""()=>{const h=document.getElementById('h'),f=document.querySelector('.foot');
                  for(let s=60;s>=34;s-=2){h.style.fontSize=s+'px'; if(h.getBoundingClientRect().bottom < f.getBoundingClientRect().top-24) break;}}""")
                pg.wait_for_timeout(100)
                out = f'{REPO}/assets/og/{slug}.png'
                pg.screenshot(path=out)
                Image.open(out).convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
                print(f'{out} — шрифт {pg.evaluate("document.getElementById(\'h\').style.fontSize")}')
            b.close()
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
        srv.shutdown()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
