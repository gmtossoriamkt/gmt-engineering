/* Отправка заявок с форм сайта на функцию Яндекс Облака (JSON).
   Адрес функции берётся из action формы (form[data-lead]). Успех показывается только при ответе {"ok":true}.
   На коды ошибок функции пользователь видит понятный текст; кнопка на время отправки блокируется. */
(function () {
  'use strict';
  var COUNTER = 113710867;
  var MAIL = 'info@gmt-engineering.ru';
  var GENERIC = 'Не удалось отправить заявку. Позвоните нам: +7 985 316-91-04 или напишите на ' + MAIL;
  var MESSAGES = {
    no_consent_pd: 'Нужно согласие на обработку персональных данных',
    no_contact: 'Укажите телефон',
    bad_phone: 'Проверьте номер телефона',
    bad_email: 'Проверьте адрес почты',
    too_large: 'Слишком длинное описание задачи — сократите его или пришлите на ' + MAIL,
    rate_limited: 'Слишком много попыток. Попробуйте позже или позвоните: +7 985 316-91-04'
  };

  function goal(name) { try { if (typeof window.ym === 'function') window.ym(COUNTER, 'reachGoal', name); } catch (e) { /* ignore */ } }

  function fields(form) {
    var o = {};
    new FormData(form).forEach(function (v, k) { if (typeof v === 'string') o[k] = v; });
    o.page = location.href.split('#')[0];
    return o;
  }

  function showError(form, text) {
    var el = form.querySelector('.form-error');
    if (!el) {
      el = document.createElement('p');
      el.className = 'form-error';
      el.setAttribute('role', 'alert');
      el.style.cssText = 'color:#B3261E;font-size:14px;margin:0;line-height:1.4';
      var btn = form.querySelector('button[type=submit]');
      form.insertBefore(el, btn);
    }
    el.textContent = text;
  }

  function bind(form) {
    form.addEventListener('submit', function (e) {
      if (!window.fetch || !window.FormData) return;
      e.preventDefault();
      if (form.dataset.sending === '1') return;
      form.dataset.sending = '1';
      var btn = form.querySelector('button[type=submit]');
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Отправляем…';
      var err = form.querySelector('.form-error'); if (err) err.textContent = '';

      fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(fields(form))
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok === true, code: j.error }; });
      }, function () { return { ok: false, code: 'network' }; }).then(function (res) {
        if (res.ok) {
          Array.prototype.forEach.call(form.children, function (el) {
            if (!el.classList.contains('ok') && el.type !== 'hidden') el.style.display = 'none';
          });
          form.querySelector('.ok').style.display = 'block';
          goal('lead');
          return;
        }
        showError(form, MESSAGES[res.code] || GENERIC);
        form.dataset.sending = '0';
        btn.disabled = false; btn.textContent = label;
      });
    });
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll('form[data-lead]'), bind); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
