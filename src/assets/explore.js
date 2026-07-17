const root = document.querySelector('[data-explore-root]');

if (root) {
  const controls = root.querySelector('[data-explore-controls]');
  const results = root.querySelector('[data-explore-results]');
  const cards = [...root.querySelectorAll('[data-explore-card]')];
  const fields = Object.fromEntries([...root.querySelectorAll('[data-filter]')].map(field => [field.dataset.filter, field]));
  const status = root.querySelector('[data-explore-status]');
  const error = root.querySelector('[data-explore-error]');
  const activeFilters = root.querySelector('[data-active-filters]');
  const empty = root.querySelector('[data-explore-empty]');
  const basePath = root.dataset.basePath;
  const defaults = { q: '', topic: '', tag: '', year: '', month: '', sort: 'published-desc' };
  const monthNames = new Intl.DateTimeFormat('en-US', { month: 'long', timeZone: 'UTC' });
  let searchIndex;
  let searchLoadFailed = false;
  let searchRun = 0;
  let debounceTimer;

  const normalizePath = value => {
    try { return new URL(value, window.location.origin).pathname.replace(/\/+$/, ''); }
    catch { return String(value || '').replace(/\/+$/, ''); }
  };

  const validOption = (field, value) => !value || [...field.options].some(option => option.value === value);

  function readUrlState() {
    const params = new URLSearchParams(window.location.search);
    const next = { ...defaults };
    for (const key of Object.keys(next)) {
      if (!params.has(key)) continue;
      const value = params.get(key) || '';
      if (key === 'q') next.q = value.slice(0, 200);
      else if (value && fields[key] && validOption(fields[key], value)) next[key] = value;
    }
    return next;
  }

  function readFormState() {
    return Object.fromEntries(Object.keys(defaults).map(key => [key, fields[key].value.trim()]));
  }

  function writeFormState(state) {
    fields.q.value = state.q;
    fields.topic.value = validOption(fields.topic, state.topic) ? state.topic : '';
    fields.tag.value = validOption(fields.tag, state.tag) ? state.tag : '';
    fields.year.value = validOption(fields.year, state.year) ? state.year : '';
    updateMonthOptions(state.year, state.month);
    fields.sort.value = [...fields.sort.options].some(option => option.value === state.sort) ? state.sort : defaults.sort;
  }

  function updateMonthOptions(year, selected = '') {
    const available = [...new Set(cards.filter(card => !year || card.dataset.year === year).map(card => card.dataset.month))].sort();
    fields.month.replaceChildren(new Option('All months', ''));
    for (const month of available) {
      const label = monthNames.format(new Date(`2020-${month}-01T00:00:00Z`));
      fields.month.add(new Option(label, month));
    }
    fields.month.disabled = !year;
    fields.month.value = year && available.includes(selected) ? selected : '';
  }

  function updateUrl(state, mode = 'replace') {
    const url = new URL(window.location.href);
    url.search = '';
    for (const [key, value] of Object.entries(state)) {
      if (value && value !== defaults[key]) url.searchParams.set(key, value);
    }
    history[mode === 'push' ? 'pushState' : 'replaceState'](null, '', url);
  }

  async function loadSearchIndex() {
    if (searchIndex || searchLoadFailed) return searchIndex;
    try {
      searchIndex = await import(`${basePath}pagefind/pagefind.js`);
      await searchIndex.init();
      return searchIndex;
    } catch (cause) {
      searchLoadFailed = true;
      console.error('Pagefind failed to load', cause);
      return undefined;
    }
  }

  const text = value => String(value || '').toLocaleLowerCase('en-US');

  function compareCards(a, b, sort, ranks) {
    const stableUrlOrder = () => a.dataset.url.localeCompare(b.dataset.url);
    if (sort === 'relevance') return (ranks.get(normalizePath(a.dataset.url)) ?? Number.MAX_SAFE_INTEGER) - (ranks.get(normalizePath(b.dataset.url)) ?? Number.MAX_SAFE_INTEGER) || stableUrlOrder();
    if (sort === 'published-asc') return a.dataset.published.localeCompare(b.dataset.published) || text(a.dataset.title).localeCompare(text(b.dataset.title)) || stableUrlOrder();
    if (sort === 'title-asc') return text(a.dataset.title).localeCompare(text(b.dataset.title)) || b.dataset.published.localeCompare(a.dataset.published) || stableUrlOrder();
    if (sort === 'updated-desc') {
      const aDate = a.dataset.updated || a.dataset.published;
      const bDate = b.dataset.updated || b.dataset.published;
      return bDate.localeCompare(aDate) || b.dataset.published.localeCompare(a.dataset.published) || text(a.dataset.title).localeCompare(text(b.dataset.title)) || stableUrlOrder();
    }
    return b.dataset.published.localeCompare(a.dataset.published) || text(a.dataset.title).localeCompare(text(b.dataset.title)) || stableUrlOrder();
  }

  function renderChips(state) {
    activeFilters.replaceChildren();
    const labels = {
      q: value => `Keyword: ${value}`,
      topic: value => `Topic: ${fields.topic.selectedOptions[0]?.textContent || value}`,
      tag: value => `Tag: ${value}`,
      year: value => `Year: ${value}`,
      month: value => `Month: ${fields.month.selectedOptions[0]?.textContent || value}`,
      sort: value => `Sort: ${fields.sort.selectedOptions[0]?.textContent || value}`
    };
    for (const [key, value] of Object.entries(state)) {
      if (!value || value === defaults[key]) continue;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'filter-chip';
      button.dataset.removeFilter = key;
      button.textContent = `${labels[key](value)} ×`;
      button.setAttribute('aria-label', `Remove ${labels[key](value)} filter`);
      activeFilters.append(button);
    }
  }

  async function applyState({ historyMode = 'replace', announce = true } = {}) {
    const state = readFormState();
    const relevanceOption = [...fields.sort.options].find(option => option.value === 'relevance');
    relevanceOption.disabled = !state.q;
    if (!state.q && state.sort === 'relevance') {
      state.sort = defaults.sort;
      fields.sort.value = defaults.sort;
    }
    const currentRun = ++searchRun;
    error.hidden = true;
    let matchingPaths;
    const ranks = new Map();

    if (state.q) {
      status.textContent = 'Searching…';
      const pagefind = await loadSearchIndex();
      if (currentRun !== searchRun) return;
      if (!pagefind) {
        matchingPaths = new Set();
        error.textContent = 'Keyword search is temporarily unavailable. Clear the keyword to keep browsing by topic, tag, and date.';
        error.hidden = false;
      } else {
        const response = await pagefind.search(state.q);
        if (currentRun !== searchRun) return;
        const resultData = await Promise.all(response.results.map(result => result.data()));
        if (currentRun !== searchRun) return;
        matchingPaths = new Set(resultData.map((result, index) => {
          const path = normalizePath(result.url);
          ranks.set(path, index);
          return path;
        }));
      }
    }

    const visible = [];
    for (const card of cards) {
      const tags = card.dataset.tags.split(',');
      const matches = (!matchingPaths || matchingPaths.has(normalizePath(card.dataset.url)))
        && (!state.topic || card.dataset.topic === state.topic)
        && (!state.tag || tags.includes(state.tag))
        && (!state.year || card.dataset.year === state.year)
        && (!state.month || card.dataset.month === state.month);
      card.hidden = !matches;
      if (matches) visible.push(card);
    }

    visible.sort((a, b) => compareCards(a, b, state.sort, ranks)).forEach(card => results.append(card));
    empty.hidden = visible.length !== 0;
    renderChips(state);
    status.textContent = `${visible.length} of ${cards.length} posts shown${state.q ? ` for “${state.q}”` : ''}.`;
    updateUrl(state, historyMode);
    if (announce) status.focus?.({ preventScroll: true });
  }

  function resetAll() {
    writeFormState(defaults);
    applyState({ historyMode: 'push' });
    fields.q.focus({ preventScroll: true });
  }

  controls.hidden = false;
  writeFormState(readUrlState());
  applyState({ announce: false });

  for (const field of Object.values(fields)) {
    if (field === fields.q) {
      field.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => applyState({ historyMode: 'replace', announce: false }), 220);
      });
    } else {
      field.addEventListener('change', () => {
        if (field === fields.year) updateMonthOptions(fields.year.value);
        applyState({ historyMode: 'push' });
      });
    }
  }

  root.addEventListener('click', event => {
    const reset = event.target.closest('[data-explore-reset]');
    if (reset) return resetAll();
    const chip = event.target.closest('[data-remove-filter]');
    if (!chip) return;
    const key = chip.dataset.removeFilter;
    fields[key].value = defaults[key];
    if (key === 'year') updateMonthOptions('');
    applyState({ historyMode: 'push' });
  });

  window.addEventListener('popstate', () => {
    writeFormState(readUrlState());
    applyState({ historyMode: 'replace' });
  });
}
