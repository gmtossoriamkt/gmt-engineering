#!/usr/bin/env python3
"""Собирает dist/ — сайт без служебных файлов. Его содержимое GitHub Actions публикует в ветку timeweb-dist,
откуда Timeweb выкладывает сайт. Всё, что не исключено здесь, будет доступно по адресу сайта.

Использование: python3 scripts/build_dist.py [папка, по умолчанию dist]
"""
import os, shutil, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Верхний уровень репозитория, который на сайт не попадает
SKIP_TOP = {'CLAUDE.md', 'README.md', 'content-plan.csv', 'factcheck', 'scripts', 'drafts', 'dist',
            'node_modules', '_og_tmp.html'}
SKIP_EXT = ('.md', '.py', '.pyc', '.bak', '.sh', '.log', '.tmp', '.csv')
NEED = ['index.html', '404.html', 'robots.txt', 'sitemap.xml', 'yandex_a8a61f28343e64fc.html']


def skip(relpath):
    parts = relpath.replace(os.sep, '/').split('/')
    if any(p.startswith('.') or p == '__pycache__' for p in parts):  # .git, .github, .claude, .gitignore
        return True
    if parts[0] in SKIP_TOP:
        return True
    return parts[-1].lower().endswith(SKIP_EXT)


def build(out):
    out = os.path.join(REPO, out)
    shutil.rmtree(out, ignore_errors=True)
    n = size = 0
    for root, dirs, files in os.walk(REPO):
        r = os.path.relpath(root, REPO)
        r = '' if r == '.' else r
        dirs[:] = [d for d in dirs if not skip(os.path.join(r, d))]
        for fn in files:
            rp = os.path.join(r, fn)
            if skip(rp):
                continue
            dst = os.path.join(out, rp)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(REPO, rp), dst)
            n += 1
            size += os.path.getsize(dst)
    miss = [f for f in NEED if not os.path.exists(os.path.join(out, f))]
    if miss:
        sys.exit('build_dist: нет обязательных файлов: ' + ', '.join(miss))
    bad = [os.path.relpath(os.path.join(rt, x), out) for rt, ds, fs in os.walk(out) for x in ds + fs
           if x.startswith('.') or x in SKIP_TOP or x.lower().endswith(SKIP_EXT)]
    if bad:
        sys.exit('build_dist: в dist попало служебное: ' + ', '.join(bad))
    print(f'build_dist: {n} файлов, {size / 1048576:.1f} МБ → {os.path.relpath(out, REPO)}/')


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'dist')
