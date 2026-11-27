**В интерактивной сессии НИКОГДА не выполнять git push без явного слова "пуш" от пользователя в текущем сообщении.**

**Агент по расписанию (skill `gmt-article`) работает только через ветки `blog/*` и PR: пуш в свою ветку `blog/*` разрешён без подтверждения, в `main` — никогда (ни коммитов, ни пуша); публикация = merge PR владельцем. Workflow в `.github/` и настройки деплоя не менять.**

# gmt-engineering.ru

Статический сайт ГМТ Инжиниринг (разработка приборов и электроники под ключ). Страницы — готовый HTML, без генератора. На каждый пуш в `main` GitHub Actions (`.github/workflows/deploy-dist.yml`) проверяет сайт (`scripts/check_blog.py`), собирает копию без служебных файлов (`scripts/build_dist.py`) и публикует её в ветку `timeweb-dist`; Timeweb App Platform (тип HTML/CSS/JS) выкладывает сайт из `timeweb-dist`, автодеплой. (Пока в настройках Timeweb не переключена ветка на `timeweb-dist`, сайт отдаётся прямо из `main` — вместе со служебными файлами.) Репозиторий на GitHub публичный — не класть сюда ничего приватного. Служебное (CLAUDE.md, content-plan.csv, factcheck/, scripts/, .claude/, .github/) на сайт не попадает; новую служебную папку — добавить в `SKIP_TOP` в `scripts/build_dist.py`.

- Главная `index.html` держит стили у себя. Внутренние страницы (блог, статьи) подключают `/assets/site.css` (со строкой версии `?v=…`, её обновлять при изменении стилей).
- Цвета брендбука: тёмно-синий `#102B3F`, циан `#00B3B3`, графит `#23272E`, светлый `#F5F7FA`. Шрифт Montserrat — локальный: `/assets/fonts.css` + `/assets/fonts/montserrat-{400..800}.woff2` (preload 400 и 600). Google Fonts не подключать.
- Контакты: +7 985 316-91-04, MAX https://max.ru/u/f9LHodD0cOLDvyS7TfGCuqMQTcuMpF-2LxGuF5nNyXHgZFoFnYUC0KjLnaQ (значок `.ic.ic-max` — картинка `/assets/max.png`, логотип MAX, в шапке рядом с телефоном, пункт в мобильном меню, блок контактов, подвал). Telegram на сайте не используется (в РФ ограничен) — не добавлять. Порядок контактов: телефон → MAX → почта; кнопка-«призрак» в первом экране внутренних страниц — «Написать в MAX», info@gmt-engineering.ru. Юрлицо ООО «Глобальные Медицинские Технологии», ОГРН 1247700287834, ИНН 9710131540.
- Яндекс Метрика 113710867 подключается ТОЛЬКО через `<script src="/assets/cookie-consent.js" defer></script>` в `<head>` (запуск после «Принять» в плашке cookie). Код счётчика и noscript-пиксель в страницы не вставлять. В подвале — ссылка `data-cookie-settings` «Настройки cookie». Цель заявки — `ym(113710867,'reachGoal','lead')`.
- Закреплённая шапка: `<script src="/assets/sticky-header.js?v=…" defer></script>` (версию обновлять при изменении скрипта) в `<head>` каждой страницы (кроме 404) — сразу после cookie-consent.js. Скрипт сам добавляет стили; шапку не дублировать вручную. Он же показывает на телефонах плавающую кнопку MAX (`.max-float`) и сворачивает меню в «☰», если пункты не помещаются в шапку (`.nav-compact`).
- Превью ссылок: `/assets/og-image.png` (1200×630) — og:image, og:site_name, twitter:card на каждой странице. У статей блога — своя обложка `/assets/og/<slug>.png` (1200×630, тёмно-синий фон, логотип, плашка рубрики, H1, «Блог · gmt-engineering.ru», схема-микросхема справа) в og:image и twitter:image.
- Форма заявок: `<form class="frm" action="https://functions.yandexcloud.net/d4epoq54usbmohm89fic" method="POST" data-lead>` + `/assets/leads.js` (JSON на функцию Яндекс Облака → письмо на info@gmt-engineering.ru через SMTP Timeweb; данные в РФ). Поля: name, phone, contact_way, task, `_subject`, `source=gmt-engineering.ru`, ловушка `_gotcha`, чекбокс `consent_pd=on`. Код функции в репозиторий не класть (репозиторий публичный).
- Сайт открыт для индексации с 21.10.2026 (robots.txt Allow + Sitemap). На новых страницах НЕ ставить meta noindex (кроме 404). Права в Яндекс.Вебмастере — файл `yandex_a8a61f28343e64fc.html` в корне, не удалять.
- Страницы услуг: `/uslugi/razrabotka-pribora/`, `/uslugi/skhemotekhnika/`, `/uslugi/proshivki/`, `/uslugi/prikladnoe-po/`, `/uslugi/korpusa-prototipy/`; отрасли `/otrasli/medicinskie-pribory/`, `/otrasli/promyshlennost/`; приборы `/pribory/datchiki/`, `/pribory/kontrollery/`, `/pribory/analizatory/`; стоимость `/stoimost/` (WebPage); конфигуратор маршрута сертификации `/marshrut/` и глоссарий `/glossarij/` (DefinedTermSet) — в подвале в меню рядом со «Стоимостью»; новые термины глоссария добавлять со ссылкой на статью; контакты `/kontakty/` — на `/assets/site.css` (классы `.page .sec .cards .split .box .formblk .frm`), JSON-LD Service + BreadcrumbList + FAQPage. Новую услугу добавлять в футер всех страниц (nav «Услуги»; отрасли и приборы — nav «Направления»), в плитки главной и в `sitemap.xml`.
- Регистрация медизделий, ПП 719, ГИСП, локализация — это сайт med-local.ru. Здесь на них только ссылаемся.

## Как добавить статью в блог

Источник тем — `content-plan.csv` (120 статей из xlsx «Контент-система ГМТ»: H1, тезис, ключи, тип, нормативка, CTA, объём). Статусы: `todo` → `in-progress` → `pr` → `done`, `skip` — не писать (причина в `note`). Пишете статью вручную — сразу ставьте ей `in-progress`, чтобы агент не взял её же. Фактчекинги редактора — `factcheck/<номер>.md`.

Полная инструкция — `.claude/skills/gmt-article/SKILL.md`. Кратко:
1. Конфиг статьи (Python-словарь `A`, вне репозитория) → `python3 scripts/new_article.py <конфиг>`: страница собирается на шаблоне последней опубликованной статьи (title до 60 знаков, description до 155, JSON-LD TechArticle + BreadcrumbList + FAQPage дословно как видимый FAQ).
2. Текст — по 6 блокам: «Коротко» (3–4 предложения, ответ на интент), нормативная база, маршрут/таблица/расчёт, кейс (реальный или с пометкой «условный пример»), FAQ 4–6 вопросов, CTA.
3. `python3 scripts/og_cover.py <slug>` — обложка `/assets/og/<slug>.png` (og:image и twitter:image уже прописаны).
4. `python3 scripts/add_blog_card.py <slug> --tags "…" --home-title "…" --home-desc "…"` — карточка первой в `blog/index.html` (`#posts`), первой в «Свежих статьях» главной (третья уходит), URL и lastmod в `sitemap.xml`.
5. Ссылка на статью в «Смотрите также» (`.rel`) профильных страниц услуг; новый термин — в `/glossarij/`.
6. При правке опубликованной статьи: dateModified в JSON-LD, lastmod в sitemap.xml и « · обновлено <дата>» в плашке даты.
7. Перед коммитом — `python3 scripts/check_blog.py --render` (0 ошибок).

Рубрики (`data-tags`, 1–2 через пробел): `razrabotka` — разработка железа, корпус, испытания (кластеры E, J); `po` — прошивки и прикладное ПО (F, G); `sert` — сертификация ТР ТС и метрология (A, B); `lokal` — локализация, реестры, госзакупки (C, D); `eaes` — ЕАЭС и экспорт (I); `otrasli` — отрасли (H); `trendy` — тренды (K).

## Проверка фактов (обязательно)

- Номера и названия ТР ТС, ГОСТ, законов, постановлений — только сверенные с первоисточником или надёжной базой (КонсультантПлюс, Гарант, Кодекс, ЕЭК). Не выдумывать пункты, баллы, сроки, цены.
- Где нормы нет — так и писать. Практика ≠ норма: помечать «как правило», «на практике».
- Кейсы без реальных данных — только с пометкой «условный пример».
- Таблицы оборачивать в `<div class="tbl">`.
