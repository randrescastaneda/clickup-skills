(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const dialog = $('#search-dialog');
  const input = $('#search-input');
  const results = $('#search-results');
  let indexPromise;
  const toast = (text) => {
    const el = $('.toast'); el.textContent = text; el.classList.add('visible');
    clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove('visible'), 2600);
  };
  const loadIndex = () => indexPromise ||= fetch(new URL('search-index.json', document.baseURI)).then((r) => { if (!r.ok) throw new Error('Search unavailable'); return r.json(); });
  const showSearch = () => {
    dialog.showModal(); input.focus();
    loadIndex().catch(() => { results.textContent = 'Search could not load. Use the sidebar to browse the documentation.'; });
  };
  $('.search-trigger').addEventListener('click', showSearch);
  $('#close-search').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => { if (e.target === dialog) { const box = dialog.getBoundingClientRect(); if (e.clientX < box.left || e.clientX > box.right || e.clientY < box.top || e.clientY > box.bottom) dialog.close(); } });
  document.addEventListener('keydown', (e) => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if (dialog.open) dialog.close(); else showSearch(); } });
  input.addEventListener('input', async () => {
    const query = input.value.trim().toLowerCase();
    if (!query) { results.textContent = 'Search by task, client, tool or setup step.'; return; }
    try {
      const index = await loadIndex(); if (input.value.trim().toLowerCase() !== query) return;
      const terms = query.split(/\s+/);
      const matches = index.map((page) => ({page, score: terms.reduce((score, term) => score + (page.title.toLowerCase().includes(term) ? 12 : 0) + (page.text.toLowerCase().includes(term) ? 1 : 0), 0)})).filter(({page}) => terms.every((term) => (page.title + ' ' + page.text).toLowerCase().includes(term))).sort((a,b) => b.score - a.score).slice(0, 9);
      results.replaceChildren();
      if (!matches.length) { results.textContent = 'No results. Try “installation”, “subtask”, “Codex” or “sync”.'; return; }
      for (const {page} of matches) {
        const a = document.createElement('a'); a.href = page.url; a.className = 'search-result';
        const title = document.createElement('strong'); title.textContent = page.title;
        const section = document.createElement('span'); section.textContent = page.section;
        const preview = document.createElement('p'); const at = page.text.toLowerCase().indexOf(terms[0]); const start = Math.max(0, at - 50); preview.textContent = (start ? '…' : '') + page.text.slice(start, start + 170) + '…';
        a.append(section, title, preview); results.append(a);
      }
    } catch { results.textContent = 'Search could not load. Browse using the sidebar.'; }
  });
  const menu = $('.menu-toggle');
  const backdrop = $('.nav-backdrop');
  const closeMenu = () => { document.body.classList.remove('nav-open'); menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','Open navigation'); backdrop.hidden = true; };
  menu.addEventListener('click', () => { const open = !document.body.classList.contains('nav-open'); if (!open) return closeMenu(); document.body.classList.add('nav-open'); menu.setAttribute('aria-expanded','true'); menu.setAttribute('aria-label','Close navigation'); backdrop.hidden = false; });
  backdrop.addEventListener('click',closeMenu);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
  document.querySelectorAll('#sidebar a').forEach((a) => a.addEventListener('click',closeMenu));
  const addCopy = (pre) => {
    if (pre.querySelector('.copy-button')) return;
    const button = document.createElement('button'); button.className = 'copy-button'; button.textContent = 'Copy'; button.type = 'button'; button.setAttribute('aria-label', 'Copy ' + (pre.querySelector('.language-prompt') ? 'agent prompt' : 'code'));
    button.addEventListener('click', async () => { try { await navigator.clipboard.writeText(pre.querySelector('code').textContent); button.textContent = 'Copied ✓'; toast('Copied to clipboard'); setTimeout(() => button.textContent = 'Copy', 2000); } catch { toast('Copy unavailable. Select and copy the text.'); } });
    pre.append(button);
  };
  document.querySelectorAll('pre').forEach(addCopy);
  document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('.filter').forEach((el) => { const active = el === button; el.classList.toggle('active',active); el.setAttribute('aria-pressed',String(active)); });
    document.querySelectorAll('.example').forEach((el) => { el.hidden = button.dataset.filter !== 'all' && el.dataset.category !== button.dataset.filter; });
  }));
  const client = $('#client-choice');
  if (client) {
    const target = $('#client-setup');
    const setupPromise = fetch(new URL('client-setups.json', document.baseURI)).then((r) => { if (!r.ok) throw new Error('Could not load'); return r.json(); });
    const showClient = async () => {
      const selected = client.value;
      try {
        const setups = await setupPromise; if (selected !== client.value) return;
        const data = setups[selected]; target.replaceChildren();
        for (const text of [data.text, data.skills]) { const p = document.createElement('p'); p.textContent = text; target.append(p); }
        const label = document.createElement('p'); label.className = 'micro-label'; label.textContent = 'RUN IN THE PLUGIN INSTALL CHECKOUT'; target.append(label);
        const pre = document.createElement('pre'); const code = document.createElement('code'); code.textContent = data.commands; pre.append(code); target.append(pre); addCopy(pre);
        if (selected !== 'claude') {
          const details = document.createElement('details'); const summary = document.createElement('summary'); summary.textContent = 'Preview the generated default MCP configuration';
          const configPre = document.createElement('pre'); const configCode = document.createElement('code'); configCode.textContent = data.config; configPre.append(configCode); details.append(summary,configPre); target.append(details); addCopy(configPre);
        }
      } catch { target.textContent = 'Setup snippets could not load. Open the Client setup matrix in the sidebar for all commands.'; }
    };
    client.addEventListener('change',showClient); showClient();
  }
  const anchors = Array.from(document.querySelectorAll('.on-this-page a[href^="#"]'));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => { for (const entry of entries) if (entry.isIntersecting) anchors.forEach((a) => a.classList.toggle('current',a.hash === '#' + entry.target.id)); },{rootMargin:'-10% 0px -75% 0px'});
    document.querySelectorAll('article h2[id]').forEach((el) => observer.observe(el));
  }
})();
