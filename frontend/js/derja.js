// Labelling desk (/derja): passphrase, then add labelled messages. The server appends each row to the Excel file.
import { $, api, h, errText } from './util.js';

const OTHER = '__other__';
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
  rows.forEach(r => list.append(h('li', {},
    h('span', { class: 'tag', text: r.intent }),
    h('span', { class: 'msg-text', text: r.text }))));
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
  renderOptions(r.data.options);
  renderRecent(r.data.recent);
  show('desk');
  return true;
}

$('#intent').addEventListener('change', toggleOther);

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
  text.focus();
  await refresh();
});

$('#logout').addEventListener('click', async () => {
  await api('/api/auth/logout', { method: 'POST' });
  show('login');
  $('#passphrase').focus();
});

refresh().then(ok => { if (!ok) $('#passphrase').focus(); });
