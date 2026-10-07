// Test report for the Kitsune agent. Data comes from data.json; the agent's replies are rendered with textContent only.
const $ = s => document.querySelector(s);
const el = (t, a = {}, ...k) => {
  const e = document.createElement(t);
  for (const [x, v] of Object.entries(a)) {
    if (x === 'class') e.className = v; else if (x === 'text') e.textContent = v; else if (x === 'html') e.innerHTML = v; else e.setAttribute(x, v);
  }
  e.append(...k.filter(Boolean));
  return e;
};
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);

function render(DATA) {
  const ev = DATA.eval, M = DATA.meta;

  // ---- scores
  const avg = rows => (100 * rows.reduce((a, r) => a + r.judge.score, 0)) / rows.length;
  const answerQ = avg(ev);
  const safety = avg(ev.filter(r => /Security|Hallucination/.test(r.category)));
  const rubric = ev.filter(r => r.rubric_pass).length;
  const halluc = ev.filter(r => r.judge.hallucination).length;
  const rets = ev.filter(r => r.retrieval);
  const top1 = rets.filter(r => r.retrieval.top1).length, top3 = rets.filter(r => r.retrieval.top3).length;
  const sec = DATA.sec, secPass = sec.filter(s => s.pass).length;
  const uiChecks = DATA.ui.checks, uiPass = uiChecks.filter(c => c.pass).length;
  const leaks = ev.filter(r => r.secret_leak).length;
  const lat = ev.map(r => r.latency).sort((a, b) => a - b);
  const p50 = lat[Math.floor(lat.length / 2)], p95 = lat[Math.floor(lat.length * 0.95)];
  const overall = Math.round(0.4 * answerQ + 0.2 * safety + 0.2 * pct(secPass, sec.length) + 0.1 * pct(top3, rets.length) + 0.1 * pct(uiPass, uiChecks.length));

  $('#lede').textContent = `I built this site so recruiters can ask an AI about my profile instead of skimming a PDF. Before pointing anyone at it, I wanted to know how often it gets things right, whether it makes things up, and whether it can be pushed off script. So I wrote ${ev.length} test questions, ran them through the same chat API the website uses, and graded every answer. I also ran ${sec.length} security checks and a browser test on desktop and mobile.`;
  $('#metaRow').append(...[M.author, `Tested ${M.date}`, `Chat model: ${M.model}`, `Grader: ${M.judge}`].map(t => el('span', { text: t })));

  const r = 80, c = 2 * Math.PI * r, col = overall >= 85 ? 'var(--good)' : overall >= 70 ? 'var(--accent)' : 'var(--bad)';
  $('#gauge').innerHTML = `<svg viewBox="0 0 200 200" role="img" aria-label="Overall score ${overall} out of 100"><circle cx="100" cy="100" r="${r}" fill="none" stroke="var(--line)" stroke-width="14"/><circle cx="100" cy="100" r="${r}" fill="none" stroke="${col}" stroke-width="14" stroke-linecap="round" stroke-dasharray="${(c * overall) / 100} ${c}" transform="rotate(-90 100 100)"/></svg><div class="num"><b>${overall}</b><span>out of 100</span></div>`;
  const tiles = [
    [`${answerQ.toFixed(0)}%`, 'Answer quality', `average grade, ${ev.length} questions`],
    [`${rubric}/${ev.length}`, 'Had every required fact', 'keyword check'],
    [`${halluc}`, 'Answers with made-up details', `${pct(halluc, ev.length)}% of replies`],
    [`${safety.toFixed(0)}%`, 'Traps and attacks handled', 'unknowns + prompt injection'],
    [`${secPass}/${sec.length}`, 'Security checks passed', `${leaks} secrets in replies`],
    [`${pct(top3, rets.length)}%`, 'Right passage retrieved', `top 3 · first place ${pct(top1, rets.length)}%`],
  ];
  $('#tiles').append(...tiles.map(([b, s, m]) => el('div', { class: 'tile' }, el('b', { text: b }), el('span', { text: s }), el('small', { text: m }))));
  $('#weights').textContent = `How the overall number is built: 40% answer quality, 20% traps and attacks, 20% security checks, 10% retrieval, 10% browser checks. Typical answer time ${p50.toFixed(1)} s (slowest 5%: ${p95.toFixed(1)} s).`;

  // ---- changes after the first run
  $('#changes').append(...DATA.changes.map(f => el('div', { class: 'finding' },
    el('span', { class: 'sev ' + (f.kind || 'good'), text: f.kind === 'low' ? 'Still open' : 'Fixed' }),
    el('div', {},
      el('h3', { text: f.title }),
      f.before ? el('p', { class: 'ba' }, el('span', { class: 'was', text: f.before }), el('span', { class: 'arrow', 'aria-hidden': 'true', text: '→' }), el('span', { class: 'now', text: f.after })) : null,
      el('p', { html: f.body })))));
  $('#strengths').append(...DATA.strengths.map(f => el('div', { class: 'finding' }, el('span', { class: 'sev good', text: 'Holds up' }), el('div', {}, el('h3', { text: f.title }), el('p', { html: f.body })))));

  // ---- category bars
  const cats = {};
  ev.forEach(r => { const k = r.category.split(':')[0]; (cats[k] ||= []).push(r); });
  $('#catBars').append(...Object.entries(cats).map(([k, rows]) => {
    const s = avg(rows), fill = el('div', { class: 'fill' });
    fill.style.width = `${s.toFixed(0)}%`;
    return el('div', { class: 'bar' }, el('span', { text: k }), el('div', { class: 'track' }, fill), el('span', { class: 'mono', text: `${s.toFixed(0)}% · ${rows.length} q` }));
  }));

  // ---- question list
  const FILTERS = [['all', 'All'], ['issues', 'Not perfect'], ...Object.keys(cats).map(k => ['cat:' + k, k])];
  let active = 'all';
  const issue = r => !r.rubric_pass || r.judge.score !== 1 || r.judge.hallucination;
  function renderQ() {
    const list = $('#qlist'); list.textContent = '';
    const rows = ev.filter(r => active === 'all' || (active === 'issues' && issue(r)) || (active.startsWith('cat:') && r.category.split(':')[0] === active.slice(4)));
    if (!rows.length) list.append(el('p', { class: 'muted', text: 'Nothing here.' }));
    rows.forEach(r => {
      const js = r.judge.score, jc = js === 1 ? 'ok' : js === 0.5 ? 'mid' : 'no';
      const pills = el('span', { class: 'pills' },
        el('span', { class: 'pill ' + jc, text: js === 1 ? 'correct' : js === 0.5 ? 'partly' : 'wrong' }),
        r.judge.hallucination ? el('span', { class: 'pill no', text: 'made-up detail' }) : null);
      const notes = [r.judge.reason, ...(r.missing && r.missing.length ? ['Missing: ' + r.missing.join(', ')] : [])].filter(Boolean);
      list.append(el('details', { class: 'q' },
        el('summary', {}, el('span', { class: 'qid', text: r.id }), el('span', { class: 'qtext', text: r.question }), pills),
        el('div', { class: 'qbody' }, el('div', { class: 'why', text: `${r.category} · answered in ${r.latency}s` }), el('div', { class: 'reply', text: r.reply }),
          notes.length ? el('div', { class: 'why', text: notes.join('  ·  ') }) : null)));
    });
  }
  const fbox = $('#filters');
  FILTERS.forEach(([k, label]) => {
    const b = el('button', { class: 'chip', type: 'button', 'aria-pressed': String(k === active), text: label });
    b.onclick = () => { active = k; fbox.querySelectorAll('.chip').forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); renderQ(); };
    fbox.append(b);
  });
  renderQ();

  // ---- screenshots
  $('#gallery').append(...M.shots.map(s => {
    const src = M.shot_base + s.file;
    const b = el('button', { type: 'button', 'aria-label': 'Enlarge: ' + s.title }, el('img', { src, alt: s.caption, loading: 'lazy' }));
    b.onclick = () => {
      const lb = el('div', { class: 'lightbox', role: 'dialog', 'aria-label': s.title }, el('div', {}, el('img', { src, alt: s.caption }), el('p', { text: s.caption })));
      const esc = e => { if (e.key === 'Escape') close(); };
      const close = () => { lb.remove(); document.removeEventListener('keydown', esc); };
      lb.onclick = close; document.addEventListener('keydown', esc); document.body.append(lb);
    };
    return el('figure', { class: s.tall ? 'tall' : '' }, b, el('figcaption', {}, el('b', { text: s.title + '. ' }), s.caption));
  }));

  // ---- security + browser
  $('#secLede').textContent = `${secPass} of ${sec.length} passed. These are plain HTTP requests against the running server: response headers, cookies, cross-site requests, access to every owner-only route, path traversal, oversized input and the rate limits.`;
  $('#secBody').append(...sec.map(s => el('tr', {}, el('td', { text: s.group }), el('td', { text: s.name }), el('td', { class: 'st ' + (s.pass ? 'ok' : 'no'), text: s.pass ? 'PASS' : 'FAIL' }), el('td', { class: 'det', text: s.detail }))));
  $('#uiBody').append(...uiChecks.map(x => el('tr', {}, el('td', { class: 'st ' + (x.pass ? 'ok' : 'no'), text: x.pass ? 'PASS' : 'FAIL' }), el('td', { text: x.name }))));
  const axe = DATA.ui.axe || { gate: [], dashboard: [] };
  [['Front screen', axe.gate], ['Dashboard', axe.dashboard]].forEach(([n, v]) => {
    $('#axe').append(el('p', {}, el('b', { text: n + ': ' }), v.length ? `${v.length} rule${v.length > 1 ? 's' : ''} failed` : 'no issues found'));
    if (v.length) $('#axe').append(el('ul', { class: 'plain' }, ...v.map(x => el('li', { text: `${x.help} (${x.impact}, ${x.nodes} element${x.nodes > 1 ? 's' : ''})` }))));
  });
  const T = DATA.ui.timings;
  $('#timings').append(el('ul', { class: 'plain' }, ...[
    `First byte: ${T.ttfb} ms`, `Page ready: ${T.dcl} ms, fully loaded ${T.load} ms`, `Page weight: ${(T.bytes / 1024).toFixed(0)} KB`,
    `A long answer in the chat, including the typing effect: ${(T.chat_roundtrip_ms / 1000).toFixed(1)} s`, `API answer time: typically ${p50.toFixed(1)} s, slowest 5% ${p95.toFixed(1)} s`].map(t => el('li', { text: t }))));
  $('#method').append(...M.method.map(t => el('li', { html: t })));
}

// ---- round 2: recruiter test on the live site (its own data file, so round 1 stays exactly as recorded)
function renderRound2(R) {
  $('#r2Date').textContent = 'Round 2 · ' + R.date;
  $('#h-r2').textContent = R.title;
  $('#r2Lede').textContent = R.lede;
  $('#r2Meta').append(...R.meta.map(t => el('span', { text: t })));
  $('#r2Tiles').append(...R.tiles.map(([b, s, m]) => el('div', { class: 'tile' }, el('b', { text: b }), el('span', { text: s }), el('small', { text: m }))));
  $('#r2Findings').append(...R.findings.map(f => el('div', { class: 'finding' },
    el('span', { class: 'sev ' + (f.status === 'watch' ? 'watch' : 'good'), text: f.status === 'watch' ? 'Watching' : 'Fixed' }),
    el('div', {},
      el('h3', { text: f.title }),
      el('p', { class: 'asked', text: 'Asked: ' + f.question }),
      el('p', { class: 'ba' }, el('span', { class: 'was', text: f.before }), el('span', { class: 'arrow', 'aria-hidden': 'true', text: '\u2192' }), el('span', { class: 'now', text: f.after })),
      el('p', { class: 'cause' }, el('b', { text: 'Why: ' }), f.cause),
      el('p', { class: 'fix' }, el('b', { text: 'Fix: ' }), f.fix)))));
  $('#r2Strengths').append(...R.strengths.map(f => el('div', { class: 'finding' }, el('span', { class: 'sev good', text: 'Holds up' }), el('div', {}, el('h3', { text: f.title }), el('p', { text: f.body })))));
  $('#r2Checks').append(...R.checks.map(c => el('tr', {}, el('td', { text: c.q }),
    el('td', { class: 'st ' + (c.result === 'pass' ? 'ok' : c.result === 'watch' ? 'watch' : 'no'), text: c.result === 'pass' ? 'PASS' : c.result === 'watch' ? 'WATCH' : 'FAIL' }),
    el('td', { class: 'det', text: c.detail }))));
  $('#r2Also').append(...R.also.map(t => el('li', { text: t })));
  $('#r2Method').append(...R.method.map(t => el('li', { text: t })));
}

// ---- round 3: an engineering fix, not a recruiter run (its own data file, same card/table components as round 2)
function renderRound3(R) {
  $('#r3Date').textContent = 'Round 3 · ' + R.date;
  $('#h-r3').textContent = R.title;
  $('#r3Lede').textContent = R.lede;
  $('#r3Meta').append(...R.meta.map(t => el('span', { text: t })));
  $('#r3Tiles').append(...R.tiles.map(([b, s, m]) => el('div', { class: 'tile' }, el('b', { text: b }), el('span', { text: s }), el('small', { text: m }))));
  $('#r3Findings').append(...R.findings.map(f => el('div', { class: 'finding' },
    el('span', { class: 'sev ' + (f.status === 'watch' ? 'watch' : 'good'), text: f.status === 'watch' ? 'Watching' : 'Fixed' }),
    el('div', {},
      el('h3', { text: f.title }),
      el('p', { class: 'asked', text: f.trigger }),
      el('p', { class: 'ba' }, el('span', { class: 'was', text: f.before }), el('span', { class: 'arrow', 'aria-hidden': 'true', text: '→' }), el('span', { class: 'now', text: f.after })),
      el('p', { class: 'cause' }, el('b', { text: 'Why: ' }), f.cause),
      el('p', { class: 'fix' }, el('b', { text: 'Fix: ' }), f.fix)))));
  $('#r3Strengths').append(...R.strengths.map(f => el('div', { class: 'finding' }, el('span', { class: 'sev good', text: 'Holds up' }), el('div', {}, el('h3', { text: f.title }), el('p', { text: f.body })))));
  $('#r3Checks').append(...R.checks.map(c => el('tr', {}, el('td', { text: c.name }),
    el('td', { class: 'st ' + (c.result === 'pass' ? 'ok' : c.result === 'watch' ? 'watch' : 'no'), text: c.result === 'pass' ? 'PASS' : c.result === 'watch' ? 'WATCH' : 'FAIL' }),
    el('td', { class: 'det', text: c.detail }))));
  $('#r3Also').append(...R.also.map(t => el('li', { text: t })));
  $('#r3Method').append(...R.method.map(t => el('li', { text: t })));
}

// ---- round 4: same card/table components as round 3
function renderRound4(R) {
  $('#r4Date').textContent = 'Round 4 · ' + R.date;
  $('#h-r4').textContent = R.title;
  $('#r4Lede').textContent = R.lede;
  $('#r4Meta').append(...R.meta.map(t => el('span', { text: t })));
  $('#r4Tiles').append(...R.tiles.map(([b, s, m]) => el('div', { class: 'tile' }, el('b', { text: b }), el('span', { text: s }), el('small', { text: m }))));
  $('#r4Findings').append(...R.findings.map(f => el('div', { class: 'finding' },
    el('span', { class: 'sev ' + (f.status === 'watch' ? 'watch' : 'good'), text: f.status === 'watch' ? 'Watching' : 'Fixed' }),
    el('div', {},
      el('h3', { text: f.title }),
      el('p', { class: 'asked', text: f.trigger }),
      el('p', { class: 'ba' }, el('span', { class: 'was', text: f.before }), el('span', { class: 'arrow', 'aria-hidden': 'true', text: '→' }), el('span', { class: 'now', text: f.after })),
      el('p', { class: 'cause' }, el('b', { text: 'Why: ' }), f.cause),
      el('p', { class: 'fix' }, el('b', { text: 'Fix: ' }), f.fix)))));
  $('#r4Strengths').append(...R.strengths.map(f => el('div', { class: 'finding' }, el('span', { class: 'sev good', text: 'Holds up' }), el('div', {}, el('h3', { text: f.title }), el('p', { text: f.body })))));
  $('#r4Checks').append(...R.checks.map(c => el('tr', {}, el('td', { text: c.name }),
    el('td', { class: 'st ' + (c.result === 'pass' ? 'ok' : c.result === 'watch' ? 'watch' : 'no'), text: c.result === 'pass' ? 'PASS' : c.result === 'watch' ? 'WATCH' : 'FAIL' }),
    el('td', { class: 'det', text: c.detail }))));
  $('#r4Also').append(...R.also.map(t => el('li', { text: t })));
  $('#r4Method').append(...R.method.map(t => el('li', { text: t })));
}

// ---- round tabs (arrow keys move between them; #round-2 in the URL opens that round)
function wireRounds() {
  const tabs = [...document.querySelectorAll('.round-tab')];
  const show = (tab, focus) => {
    tabs.forEach(t => { const on = t === tab; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; document.getElementById(t.getAttribute('aria-controls')).hidden = !on; });
    if (focus) tab.focus();
    history.replaceState(null, '', '#' + tab.getAttribute('aria-controls'));
  };
  tabs.forEach((t, i) => {
    t.onclick = () => show(t);
    t.onkeydown = e => { const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (d) { e.preventDefault(); show(tabs[(i + d + tabs.length) % tabs.length], true); } };
  });
  const start = tabs.find(t => '#' + t.getAttribute('aria-controls') === location.hash);
  if (start) show(start);
}
wireRounds();
fetch('/static/report/round2.json').then(r => r.json()).then(renderRound2)
  .catch(() => { $('#r2Lede').textContent = 'The round 2 data could not be loaded. Refresh the page to try again.'; });
fetch('/static/report/round3.json').then(r => r.json()).then(renderRound3)
  .catch(() => { $('#r3Lede').textContent = 'The round 3 data could not be loaded. Refresh the page to try again.'; });
fetch('/static/report/round4.json').then(r => r.json()).then(renderRound4)
  .catch(() => { $('#r4Lede').textContent = 'The round 4 data could not be loaded. Refresh the page to try again.'; });

const embedded = document.getElementById('report-data');
(embedded ? Promise.resolve(JSON.parse(embedded.textContent)) : fetch('/static/report/data.json').then(r => r.json()))
  .then(render)
  .catch(() => { $('#lede').textContent = 'The report data could not be loaded. Refresh the page to try again.'; });
