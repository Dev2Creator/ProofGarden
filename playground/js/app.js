/* UI wiring for the ProofGarden playground. */

(() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  /* ------------------------------------------------------------- theming */
  const themeButton = $('#theme-toggle');
  const storedTheme = localStorage.getItem('pg-theme');
  if (storedTheme) document.documentElement.dataset.theme = storedTheme;
  themeButton.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('pg-theme', next);
  });

  /* ---------------------------------------------------------------- tabs */
  const tabs = $$('.tab');
  const panels = $$('.panel');
  function activate(id) {
    tabs.forEach((tab) => {
      const selected = tab.id === `tab-${id}`;
      tab.setAttribute('aria-selected', String(selected));
    });
    panels.forEach((panel) => {
      panel.hidden = panel.id !== `panel-${id}`;
    });
  }
  tabs.forEach((tab) => tab.addEventListener('click', () => activate(tab.id.replace('tab-', ''))));
  tabs.forEach((tab) => tab.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const index = tabs.indexOf(tab);
    const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : (index - 1 + tabs.length) % tabs.length;
    tabs[next].focus();
    activate(tabs[next].id.replace('tab-', ''));
  }));

  /* ----------------------------------------------------------- logic lab */
  const logicForm = $('#logic-form');
  const logicInput = $('#logic-input');
  const logicError = $('#logic-error');
  const logicOutput = $('#logic-output');

  function renderLogic(formula) {
    logicError.hidden = true;
    try {
      const expr = LogicLab.parse(formula);
      const table = LogicLab.truthTable(expr);
      const header = [...table.names, 'result'].map((h) => `<th scope="col">${h}</th>`).join('');
      const rows = table.rows.map((row) => {
        const cells = table.names.map((n) => `<td>${row.env[n] ? 'T' : 'F'}</td>`).join('');
        return `<tr>${cells}<td class="${row.result ? 'ok' : 'bad'}">${row.result ? 'T' : 'F'}</td></tr>`;
      }).join('');
      logicOutput.innerHTML = `
        <p class="classification ${table.classification}">${table.classification}</p>
        <table class="truth"><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table>`;
    } catch (error) {
      logicOutput.innerHTML = '';
      logicError.textContent = error.message;
      logicError.hidden = false;
    }
  }

  logicForm.addEventListener('submit', (event) => {
    event.preventDefault();
    renderLogic(logicInput.value);
  });
  $('#logic-example').addEventListener('click', () => {
    logicInput.value = 'NOT (P AND Q) IFF ((NOT P) OR (NOT Q))';
    renderLogic(logicInput.value);
  });
  renderLogic(logicInput.value);

  /* ------------------------------------------------------- model helpers */
  const models = window.PG_MODELS;
  const byId = Object.fromEntries(models.map((m) => [m.id, m]));

  function fillSelect(select) {
    select.innerHTML = models.map((m) => `<option value="${m.id}">${m.name}</option>`).join('');
  }
  ['#machine-select', '#checker-select', '#invariant-select', '#temporal-select'].forEach((sel) => fillSelect($(sel)));

  function stateLabel(state) {
    return Object.entries(state).map(([k, v]) => `${k}=${v}`).join(', ');
  }

  /* -------------------------------------------------- state machine graph */
  const graph = $('#machine-graph');
  const detail = $('#machine-detail');

  function renderGraph(modelId) {
    const model = byId[modelId];
    $('#machine-description').textContent = model.description;
    const states = [];
    const seen = new Set();
    const push = (state) => {
      const key = JSON.stringify(Object.entries(state).sort());
      if (!seen.has(key)) { seen.add(key); states.push({ key, state }); }
    };
    model.initial.forEach(push);
    model.edges.forEach((e) => { push(e.from); push(e.to); });

    const width = 520, height = 360, radius = Math.min(width, height) / 2 - 70;
    const cx = width / 2, cy = height / 2;
    const positions = {};
    states.forEach((entry, index) => {
      const angle = (2 * Math.PI * index) / states.length - Math.PI / 2;
      positions[entry.key] = {
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle)
      };
    });

    const edgeMarkup = model.edges.map((edge) => {
      const fromKey = JSON.stringify(Object.entries(edge.from).sort());
      const toKey = JSON.stringify(Object.entries(edge.to).sort());
      const from = positions[fromKey], to = positions[toKey];
      if (!from || !to) return '';
      if (fromKey === toKey) {
        return `<path class="edge" d="M ${from.x} ${from.y - 18} a 22 22 0 1 1 0.1 0" marker-end="url(#arrow)" />`;
      }
      const dx = to.x - from.x, dy = to.y - from.y;
      const dist = Math.hypot(dx, dy) || 1;
      const offset = 26;
      const x1 = from.x + (dx / dist) * offset, y1 = from.y + (dy / dist) * offset;
      const x2 = to.x - (dx / dist) * offset, y2 = to.y - (dy / dist) * offset;
      return `<line class="edge" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#arrow)"><title>${edge.label}</title></line>`;
    }).join('');

    const nodeMarkup = states.map(({ key, state }) => {
      const pos = positions[key];
      const isInitial = model.initial.some((s) => JSON.stringify(Object.entries(s).sort()) === key);
      return `<g class="node ${isInitial ? 'initial' : ''}" tabindex="0" role="button" data-key="${encodeURIComponent(key)}" transform="translate(${pos.x} ${pos.y})">
        <circle r="24"></circle>
        <text y="4">${isInitial ? '◉' : '•'}</text>
        <title>${stateLabel(state)}</title>
      </g>`;
    }).join('');

    graph.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="auto" aria-label="State graph for ${model.name}">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path>
        </marker>
      </defs>
      ${edgeMarkup}
      ${nodeMarkup}
    </svg>`;

    const showDetail = (key) => {
      const state = JSON.parse(key);
      const outgoing = model.edges.filter((e) => JSON.stringify(Object.entries(e.from).sort()) === key);
      detail.innerHTML = `
        <h3>${stateLabel(state)}</h3>
        <p class="muted">${outgoing.length ? `${outgoing.length} outgoing transition(s)` : 'No outgoing transitions (deadlock in this model).'}</p>
        <ul class="plain">${outgoing.map((e) => `<li><code>${e.label}</code> → ${stateLabel(e.to)}</li>`).join('')}</ul>`;
      $$('#machine-graph .node').forEach((node) => node.classList.remove('active'));
      const active = graph.querySelector(`.node[data-key="${encodeURIComponent(key)}"]`);
      if (active) active.classList.add('active');
    };

    $$('#machine-graph .node').forEach((node) => {
      node.addEventListener('click', () => showDetail(decodeURIComponent(node.dataset.key)));
      node.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          showDetail(decodeURIComponent(node.dataset.key));
        }
      });
    });
  }

  $('#machine-select').addEventListener('change', (event) => renderGraph(event.target.value));
  renderGraph('traffic_light');

  /* ------------------------------------------------------ model checking */
  function renderChecker() {
    const model = byId[$('#checker-select').value];
    const limit = Math.max(1, Number($('#checker-limit').value) || 5000);
    const result = ModelChecker.explore(model, limit);

    const invariantCards = model.invariants.map((inv) => {
      const check = ModelChecker.checkInvariant(result, inv);
      return card(inv.name, check);
    }).join('');
    const deadlock = ModelChecker.checkDeadlock(result);

    $('#checker-output').innerHTML = `
      <div class="summary">
        <span><strong>${result.order.length}</strong> states</span>
        <span><strong>${result.edges.length}</strong> transitions</span>
        <span><strong>${result.deadlocks.length}</strong> deadlocks</span>
        <span class="${result.complete ? 'ok' : 'bad'}">${result.complete ? 'complete' : 'incomplete'}</span>
      </div>
      ${result.stopReason ? `<p class="error">Exploration stopped: ${result.stopReason}. No claim is made about the model.</p>` : ''}
      ${invariantCards || '<p class="muted">This model declares no invariants.</p>'}
      ${card('deadlock freedom', deadlock)}
    `;
  }

  function card(name, check) {
    const trace = check.trace && check.trace.length
      ? `<ol class="trace">${check.trace.map((step) => `<li>${stateLabel(step.state)} <span class="muted">← ${step.label || 'initial'}</span></li>`).join('')}</ol>`
      : '';
    return `<article class="card ${check.outcome}">
      <header><h3>${name}</h3><span class="badge">${check.outcome}</span></header>
      <p>${check.message}</p>
      ${trace}
    </article>`;
  }

  $('#checker-run').addEventListener('click', renderChecker);
  $('#checker-select').addEventListener('change', renderChecker);
  renderChecker();

  /* ------------------------------------------------- invariant playground */
  function renderInvariant() {
    const model = byId[$('#invariant-select').value];
    const repair = $('#invariant-repair').checked;
    const isForbidden = (state) => model.invariants.some((inv) =>
      Object.entries(inv.forbidden).every(([k, v]) => state[k] === v));
    const effective = repair
      ? { ...model, edges: model.edges.filter((edge) => !isForbidden(edge.to)) }
      : model;
    const result = ModelChecker.explore(effective, 5000);
    const cards = model.invariants.map((inv) => card(inv.name, ModelChecker.checkInvariant(result, inv))).join('');
    $('#invariant-output').innerHTML = `
      <p class="muted">${repair ? 'Repaired model: transitions into forbidden states were removed.' : 'Original model, bugs included.'} ${result.order.length} reachable states.</p>
      ${cards || '<p class="muted">This model declares no invariants.</p>'}`;
  }
  $('#invariant-select').addEventListener('change', renderInvariant);
  $('#invariant-repair').addEventListener('change', renderInvariant);
  renderInvariant();

  /* ------------------------------------------------------ temporal logic */
  $('#temporal-run').addEventListener('click', () => {
    const model = byId[$('#temporal-select').value];
    const result = ModelChecker.explore(model, 5000);
    const p = ModelChecker.predicateFromText($('#temporal-p').value);
    const q = ModelChecker.predicateFromText($('#temporal-q').value);
    const g = ModelChecker.always(result, p);
    const f = ModelChecker.eventually(result, p);
    const u = ModelChecker.until(result, p, q);
    $('#temporal-output').innerHTML = `
      <article class="card">
        <h3>Results over ${result.order.length} reachable states</h3>
        <ul class="plain">
          <li><strong>G p</strong> (always): ${g ? 'true' : 'false'} — p holds in every reachable state</li>
          <li><strong>F p</strong> (eventually): ${f ? 'true' : 'false'} — some reachable state satisfies p</li>
          <li><strong>p U q</strong> (until): ${u === null ? 'unknown (incomplete exploration)' : (u ? 'true' : 'false')}</li>
        </ul>
        <p class="muted">Safety ≈ G ¬bad. Liveness needs fairness assumptions that this bounded explorer does not model.</p>
      </article>`;
  });

  /* ---------------------------------------------------------- curriculum */
  const lessons = [
    '01 · Propositional logic: syntax, truth tables, tautologies',
    '02 · Implication, equivalence and De Morgan’s laws',
    '03 · Predicate logic and quantifiers',
    '04 · Sets, relations and functions',
    '05 · State machines and reachability',
    '06 · Invariants and safety properties',
    '07 · Hoare triples and weakest preconditions',
    '08 · Bounded model checking and counterexamples',
    '09 · Temporal logic: safety vs liveness',
    '10 · Concurrency and interleaving'
  ];
  const done = new Set(JSON.parse(localStorage.getItem('pg-progress') || '[]'));
  const list = $('#curriculum-list');
  list.innerHTML = lessons.map((lesson, index) => `
    <li>
      <label class="check">
        <input type="checkbox" data-index="${index}" ${done.has(index) ? 'checked' : ''} />
        <span>${lesson}</span>
      </label>
    </li>`).join('');
  list.addEventListener('change', (event) => {
    const index = Number(event.target.dataset.index);
    if (event.target.checked) done.add(index); else done.delete(index);
    localStorage.setItem('pg-progress', JSON.stringify([...done]));
  });
})();
