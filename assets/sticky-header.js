/* Закреплённая верхняя плашка (логотип, меню, телефон, кнопка) на всех страницах.
   Пока шапка на экране — всё как в вёрстке. Когда плашка уходит за верх экрана, она фиксируется
   вверху (класс .is-fixed), а на её месте остаётся заглушка той же высоты, чтобы контент не прыгал.
   Мобильное меню (.mnav) в закреплённом состоянии открывается под плашкой.
   Стили подключаются этим же скриптом — одинаково для главной и внутренних страниц. */
(function () {
  'use strict';

  var css =
    'html{scroll-padding-top:88px}' +
    '.topbar-spacer{display:none}' +
    '.topbar.is-fixed{position:fixed;top:8px;left:16px;right:16px;z-index:150;padding:8px;background:rgba(16,43,63,.97);border-radius:44px;box-shadow:0 10px 30px rgba(11,33,51,.28);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);animation:gmtSlide .22s ease-out}' +
    '.topbar.is-fixed .navpill,.topbar.is-fixed .contactpill{min-height:56px}' +
    '.topbar.is-fixed>.btn{min-height:56px;padding:0 26px;font-size:16px}' +
    '.shell.has-fixed .topbar-spacer{display:block}' +
    '.shell.has-fixed.open .mnav{position:fixed;left:16px;right:16px;top:calc(var(--sticky-h,72px) + 4px);z-index:149;margin:0;max-height:calc(100vh - var(--sticky-h,72px) - 20px);overflow:auto;box-shadow:0 10px 30px rgba(11,33,51,.28)}' +
    '@keyframes gmtSlide{from{transform:translateY(-110%)}to{transform:none}}' +
    '@media (max-width:720px){html{scroll-padding-top:72px}.topbar.is-fixed{top:6px;left:8px;right:8px;padding:6px;border-radius:34px}.shell.has-fixed.open .mnav{left:8px;right:8px}}' +
    '@media (prefers-reduced-motion:reduce){.topbar.is-fixed{animation:none}}' +
    /* простая шапка (политика конфиденциальности) */
    'body>header{position:sticky;top:0;z-index:100}';

  var style = document.createElement('style');
  style.id = 'sticky-header-style';
  style.textContent = css;
  document.head.appendChild(style);

  function init() {
    var shell = document.querySelector('.shell');
    var bar = shell && shell.querySelector('.topbar');
    if (!bar) return;

    var spacer = document.createElement('div');
    spacer.className = 'topbar-spacer';
    spacer.setAttribute('aria-hidden', 'true');
    bar.parentNode.insertBefore(spacer, bar);

    var fixed = false;
    var naturalH = bar.offsetHeight;

    function setVar() {
      var h = fixed ? bar.getBoundingClientRect().bottom + 8 : 0;
      document.documentElement.style.setProperty('--sticky-h', Math.round(h) + 'px');
    }

    function update() {
      // граница — низ плашки в обычном положении (по заглушке, если плашка уже закреплена)
      var ref = fixed ? spacer : bar;
      var bottom = ref.getBoundingClientRect().bottom;
      var shouldFix = bottom < 0;
      if (shouldFix !== fixed) {
        if (shouldFix) {
          naturalH = bar.offsetHeight;
          spacer.style.height = naturalH + 'px';
        }
        fixed = shouldFix;
        bar.classList.toggle('is-fixed', fixed);
        shell.classList.toggle('has-fixed', fixed);
      }
      setVar();
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { ticking = false; update(); });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () {
      if (!fixed) naturalH = bar.offsetHeight;
      else spacer.style.height = naturalH + 'px';
      onScroll();
    });

    // мобильное меню закрывается по клику на пункт
    Array.prototype.forEach.call(shell.querySelectorAll('.mnav a'), function (a) {
      a.addEventListener('click', function () { shell.classList.remove('open'); });
    });

    update();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
