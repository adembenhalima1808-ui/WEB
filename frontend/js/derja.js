// Labelling desk (/derja): passphrase, then add labelled messages. The server appends each row to the Excel file.
import { $, api, h, errText } from './util.js';

const OTHER = '__other__';
const LOW = 20;   // types with fewer saved examples than this are highlighted
// Same rules as the server (app/labeler.py), only to show the person what will be stored.
const ARABIC = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/;
const LATIN = /[A-Za-zÀ-ÖØ-öø-ÿ]/;
const SCRIPT_LABEL = { arabic: 'Arabic letters', arabizi: 'Arabizi (Latin letters)', mixed: 'Mixed Arabic and Latin' };
let labels = {};
const loginPanel = $('#login');
const workspace = $('#workspace');

function show(panel) {
  loginPanel.classList.toggle('hide', panel !== 'login');
  workspace.classList.toggle('hide', panel !== 'desk');
}

function renderRecent(rows) {
  const list = $('#recent');
  list.textContent = '';
  if (!rows.length) { list.append(h('li', { class: 'recent-empty', text: 'No messages yet.' })); return; }
  rows.forEach((r, i) => list.append(h('li', {},
    h('div', { class: 'row-head' },
      h('span', { class: 'tag', text: `${labels[r.intent] || r.intent} · ${r.script}` }),
      i === 0 ? h('button', { class: 'btn undo', type: 'button', text: 'Remove', onclick: () => undo(r.text) }) : null),
    h('span', { class: 'msg-text', dir: 'auto', text: r.text }))));
}

function renderCounts(options, summary) {
  const list = $('#counts');
  list.textContent = '';
  options.forEach(o => {
    const n = summary.intents[o.value] || 0;
    list.append(h('li', { class: n < LOW ? 'low' : '' }, h('b', { text: String(n) }), ` ${o.label}`));
  });
  const scripts = Object.entries(summary.scripts).map(([k, n]) => `${n} ${k}`).join(' · ');
  if (scripts) list.append(h('li', {}, scripts));
}

function scriptOf(text) {
  const a = ARABIC.test(text), l = LATIN.test(text);
  return a && l ? 'mixed' : a ? 'arabic' : l ? 'arabizi' : '';
}

function updateHint() {
  const script = scriptOf($('#text').value);
  $('#script-hint').textContent = script ? `Detected: ${SCRIPT_LABEL[script]}. Ctrl+Enter saves.` : 'Ctrl+Enter saves.';
}

function renderOptions(options) {
  const select = $('#intent');
  const keep = select.value;
  select.textContent = '';
  select.append(h('option', { value: '', text: 'Choose one…', disabled: true }));
  options.forEach(o => select.append(h('option', { value: o.value, text: o.label })));
  select.append(h('option', { value: OTHER, text: 'Other (type my own)' }));
  select.value = keep && [...select.options].some(o => o.value === keep) ? keep : '';
  toggleOther();
}

function toggleOther() {
  const isOther = $('#intent').value === OTHER;
  $('#other-box').classList.toggle('hide', !isOther);
  if (!isOther) $('#intent-other').value = '';
}

// Pulls the file's current state. Returns false (and shows the passphrase form) when the session is gone.
async function refresh() {
  const r = await api('/api/derja/state');
  if (!r.ok) { show('login'); return false; }
  const n = r.data.count;
  $('#count').textContent = `${n} message${n === 1 ? '' : 's'} saved`;
  labels = Object.fromEntries(r.data.options.map(o => [o.value, o.label]));
  renderOptions(r.data.options);
  renderCounts(r.data.options, r.data.summary);
  renderRecent(r.data.recent);
  show('desk');
  return true;
}

// Removes the newest row (for a wrong type or a typo). The server checks it is still the newest one.
async function undo(text) {
  const err = $('#add-err');
  err.textContent = '';
  const r = await api('/api/derja/undo', { method: 'POST', body: { text } });
  if (r.status === 401) { show('login'); return; }
  if (!r.ok) err.textContent = errText(r);
  await refresh();
}

$('#intent').addEventListener('change', toggleOther);
$('#text').addEventListener('input', updateHint);
$('#text').addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); $('#add-form').requestSubmit(); }
});

$('#login-form').addEventListener('submit', async e => {
  e.preventDefault();
  const err = $('#login-err');
  const pass = $('#passphrase');
  const btn = $('button', $('#login-form'));
  err.textContent = '';
  btn.disabled = true;
  const r = await api('/api/derja/login', { method: 'POST', body: { passphrase: pass.value } });
  btn.disabled = false;
  if (!r.ok) { err.textContent = errText(r); return; }
  pass.value = '';
  if (!await refresh()) err.textContent = 'Could not open the desk. Try again.';
});

$('#add-form').addEventListener('submit', async e => {
  e.preventDefault();
  const err = $('#add-err');
  const btn = $('#add-btn');
  const text = $('#text');
  const choice = $('#intent').value;
  const intent = choice === OTHER ? $('#intent-other').value.trim() : choice;
  err.textContent = '';
  if (!intent) { err.textContent = choice === OTHER ? 'Type a short name for the type.' : 'Choose a type from the list.'; return; }
  btn.disabled = true;
  const r = await api('/api/derja/add', { method: 'POST', body: { text: text.value.trim(), intent } });
  btn.disabled = false;
  if (r.status === 401) {
    show('login');
    $('#login-err').textContent = 'Your session ended. Enter the passphrase again.';
    return;
  }
  if (!r.ok) { err.textContent = errText(r); return; }
  // The chosen type stays selected, so labelling a run of similar messages is quick.
  text.value = '';
  updateHint();
  text.focus();
  await refresh();
});

$('#logout').addEventListener('click', async () => {
  await api('/api/auth/logout', { method: 'POST' });
  show('login');
  $('#passphrase').focus();
});

refresh().then(ok => { if (!ok) $('#passphrase').focus(); });
