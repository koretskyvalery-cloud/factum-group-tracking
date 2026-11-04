// Общая навигация Factum Group Tracking: Главная · Приборы · Цели.
// Десктоп — панель сверху (в ширину контента); телефон — закреплённая панель внизу под большой палец.
// На страницах отделов — вторая строка-переключатель отделов. Подключается одной строкой: <script src="nav.js"></script>
(function () {
  const file = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const DEPTS = [
    ['factum-auto-sales.html', 'Продажи'],
    ['factum-auto-marketing.html', 'Маркетинг'],
    ['factum-auto-hr.html', 'HR'],
    ['factum-auto-finance.html', 'Финансы'],
    ['factum-finotdel.html', 'Финотдел'],
  ];
  const isHome = file === '' || file === 'index.html';
  const isGoals = file === 'goals.html';
  const dept = DEPTS.find(d => d[0] === file);
  const isDash = file === 'factum-auto.html' || !!dept;

  const css = `
  .fgt-nav { position: sticky; top: 0; z-index: 60; margin: 0 auto 16px; max-width: var(--fgt-w, 1060px);
    display: flex; align-items: center; gap: 2px; padding: 5px 6px 5px 14px;
    background: var(--surface-1, #fcfcfb); border: 1px solid var(--border, rgba(11,11,11,.1)); border-radius: 999px;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  .fgt-brand { font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
    color: var(--text-muted, #898781); text-decoration: none; margin-right: 12px; white-space: nowrap; }
  .fgt-nav > a:not(.fgt-brand) { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 600;
    color: var(--text-secondary, #52514e); text-decoration: none; padding: 6px 13px; border-radius: 999px; white-space: nowrap; }
  .fgt-nav > a:not(.fgt-brand):hover { color: var(--text-primary, #0b0b0b); }
  .fgt-nav > a.on { color: var(--text-primary, #0b0b0b); background: color-mix(in srgb, var(--series-1, #2a78d6) 14%, var(--surface-1, #fcfcfb)); }
  .fgt-nav svg { width: 16px; height: 16px; flex: none; }
  .fgt-sub { max-width: var(--fgt-w, 1060px); margin: -6px auto 16px; display: flex; gap: 6px; flex-wrap: wrap; padding: 0 2px;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  .fgt-sub a { font-size: 12px; color: var(--text-secondary, #52514e); text-decoration: none; padding: 4px 11px; border-radius: 999px;
    border: 1px solid var(--border, rgba(11,11,11,.1)); white-space: nowrap; }
  .fgt-sub a:hover { color: var(--text-primary, #0b0b0b); }
  .fgt-sub a.on { background: color-mix(in srgb, var(--series-1, #2a78d6) 14%, var(--surface-1, #fcfcfb));
    border-color: color-mix(in srgb, var(--series-1, #2a78d6) 40%, var(--surface-1, #fcfcfb)); color: var(--text-primary, #0b0b0b); font-weight: 600; }
  @media (max-width: 720px) {
    body.has-fgt-nav { padding-bottom: 92px !important; }
    .fgt-nav { position: fixed; left: 0; right: 0; bottom: 0; top: auto; max-width: none; margin: 0; border-radius: 0;
      border: 0; border-top: 1px solid var(--border, rgba(11,11,11,.1)); display: grid; grid-template-columns: repeat(3, 1fr);
      padding: 6px 8px calc(8px + env(safe-area-inset-bottom, 0px)); }
    .fgt-brand { display: none; }
    .fgt-nav > a:not(.fgt-brand) { flex-direction: column; gap: 3px; font-size: 11px; padding: 4px 0; border-radius: 10px; justify-content: center; }
    .fgt-nav > a.on { background: none; color: var(--series-1, #2a78d6); }
    .fgt-nav svg { width: 22px; height: 22px; }
    .fgt-sub { flex-wrap: nowrap; overflow-x: auto; margin: 0 -8px 14px; padding: 0 8px 4px; scrollbar-width: none; }
    .fgt-sub::-webkit-scrollbar { display: none; }
  }`;

  const ic = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/></svg>',
    gauge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18a9 9 0 1 1 16 0"/><path d="M12 14l4-5"/><circle cx="12" cy="15" r="1.3" fill="currentColor"/></svg>',
    goal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>',
  };
  const a = (href, on, icon, label) => `<a href="${href}"${on ? ' class="on"' : ''}>${icon}<span>${label}</span></a>`;
  const bar = `<nav class="fgt-nav" aria-label="Разделы">
    <a class="fgt-brand" href="index.html">Factum Group Tracking</a>
    ${a('index.html', isHome, ic.home, 'Главная')}${a('factum-auto.html', isDash, ic.gauge, 'Приборы')}${a('goals.html', isGoals, ic.goal, 'Цели')}
  </nav>`;
  const sub = isDash ? `<div class="fgt-sub" aria-label="Отделы">${DEPTS.map(d =>
    `<a href="${d[0]}"${file === d[0] ? ' class="on"' : ''}>${d[1]}</a>`).join('')}</div>` : '';

  function mount() {
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    const wrap = document.querySelector('.wrap');
    if (wrap) { const mw = getComputedStyle(wrap).maxWidth; if (mw && mw !== 'none') document.documentElement.style.setProperty('--fgt-w', mw); }
    document.body.insertAdjacentHTML('afterbegin', bar + sub);
    document.body.classList.add('has-fgt-nav');
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
