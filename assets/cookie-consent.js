/* Согласие на cookie и запуск Яндекс Метрики только после согласия (как на med-local.ru).
   Выбор хранится в localStorage (ключ cookieConsent). До «Принять» и после «Отклонить»
   Метрика не загружается и её cookie не ставятся. Изменить выбор — ссылка с атрибутом
   data-cookie-settings (в подвале и в Политике конфиденциальности). */
(function () {
  'use strict';

  var KEY = 'cookieConsent';
  var METRIKA_ID = 113710867;
  var T = {
    label: 'Уведомление об использовании cookie',
    text: 'Мы используем cookie и Яндекс Метрику (вебвизор, карта кликов), чтобы анализировать и улучшать сайт. Аналитика включается только с вашего согласия. Подробнее — в <a href="/privacy/#cookies">Политике конфиденциальности</a>.',
    accept: 'Принять',
    decline: 'Отклонить'
  };

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY));
      return v && (v.v === 'granted' || v.v === 'denied') ? v.v : null;
    } catch (e) { return null; }
  }
  function write(value) {
    try { localStorage.setItem(KEY, JSON.stringify({ v: value, t: new Date().toISOString() })); } catch (e) { /* без хранилища выбор не запомнится */ }
  }

  var metrikaLoaded = false;
  function loadMetrika() {
    if (metrikaLoaded) return;
    metrikaLoaded = true;
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      for (var j = 0; j < document.scripts.length; j++) { if (document.scripts[j].src === r) { return; } }
      k = e.createElement(t); a = e.getElementsByTagName(t)[0]; k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js?id=' + METRIKA_ID, 'ym');
    window.ym(METRIKA_ID, 'init', { ssr: true, webvisor: true, clickmap: true, ecommerce: 'dataLayer', referrer: document.referrer, url: location.href, accurateTrackBounce: true, trackLinks: true });
  }

  function clearMetrikaData() {
    var host = location.hostname, parts = host.split('.'), domains = [host, '.' + host];
    if (parts.length > 2) domains.push('.' + parts.slice(-2).join('.'));
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (!/^_ym/.test(name)) return;
      domains.forEach(function (d) { document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=' + d; });
      document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    });
    try {
      Object.keys(localStorage).forEach(function (k) { if (/^_ym/.test(k)) localStorage.removeItem(k); });
      Object.keys(sessionStorage).forEach(function (k) { if (/^_ym/.test(k)) sessionStorage.removeItem(k); });
    } catch (e) { /* ignore */ }
  }

  function addStyles() {
    if (document.getElementById('cookie-consent-style')) return;
    var s = document.createElement('style');
    s.id = 'cookie-consent-style';
    s.textContent =
      '#cookie-consent-banner{position:fixed;left:16px;right:16px;bottom:16px;z-index:200;max-width:1100px;margin:0 auto;background:#102B3F;color:#C9D6E2;border:1px solid #1E4561;border-radius:20px;padding:18px 22px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;font-family:"Montserrat",system-ui,sans-serif;font-size:14px;line-height:1.5;box-shadow:0 12px 32px rgba(11,33,51,.35)}' +
      '#cookie-consent-banner p{margin:0;flex:1;min-width:240px}' +
      '#cookie-consent-banner a{color:#7FD9D9;text-decoration:underline}' +
      '#cookie-consent-banner .cc-btns{display:flex;gap:10px;flex-wrap:wrap}' +
      '#cookie-consent-banner button{border-radius:999px;min-height:44px;padding:0 22px;min-width:120px;font:600 14px "Montserrat",system-ui,sans-serif;cursor:pointer;white-space:nowrap;border:1.5px solid #00B3B3}' +
      '#cookie-consent-banner .cc-accept{background:#00B3B3;color:#102B3F}' +
      '#cookie-consent-banner .cc-accept:hover{background:#19C7C7}' +
      '#cookie-consent-banner .cc-decline{background:transparent;color:#fff}' +
      '#cookie-consent-banner .cc-decline:hover{border-color:#7FD9D9;color:#7FD9D9}' +
      '@media(max-width:600px){#cookie-consent-banner{left:8px;right:8px;bottom:8px;padding:16px}#cookie-consent-banner .cc-btns{width:100%}#cookie-consent-banner button{flex:1}}';
    document.head.appendChild(s);
  }

  function hide() {
    var b = document.getElementById('cookie-consent-banner');
    if (b && b.parentNode) b.parentNode.removeChild(b);
  }

  function choose(value) {
    var before = read();
    write(value);
    hide();
    if (value === 'granted') {
      loadMetrika();
    } else {
      clearMetrikaData();
      if (before === 'granted' && metrikaLoaded) location.reload(); // остановить уже загруженный счётчик
    }
  }

  function show() {
    if (document.getElementById('cookie-consent-banner')) return;
    addStyles();
    var b = document.createElement('div');
    b.id = 'cookie-consent-banner';
    b.setAttribute('role', 'region');
    b.setAttribute('aria-label', T.label);
    b.innerHTML = '<p>' + T.text + '</p><div class="cc-btns">' +
      '<button type="button" class="cc-accept">' + T.accept + '</button>' +
      '<button type="button" class="cc-decline">' + T.decline + '</button></div>';
    document.body.appendChild(b);
    b.querySelector('.cc-accept').addEventListener('click', function () { choose('granted'); });
    b.querySelector('.cc-decline').addEventListener('click', function () { choose('denied'); });
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('[data-cookie-settings]') : null;
    if (a) { e.preventDefault(); show(); }
  });

  function start() {
    var state = read();
    if (state === 'granted') loadMetrika();
    else if (state === null) show();
  }
  if (document.body) start();
  else document.addEventListener('DOMContentLoaded', start);
})();
