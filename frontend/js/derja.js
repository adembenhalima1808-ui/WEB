// Labelling desk (/derja): passphrase, then add labelled messages. The server appends each row to the Excel file.
import { $, api, h, errText } from './util.js';

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
    h('span', { class: 'tag', text: `${r.intent} · ${r.script}` }),
    h('span', { class: 'msg-text', text: r.text }))));
}

function renderIntents(intents) {
  const list = $('#intent-list');
  list.textContent = '';
  intents.forEach(i => list.append(h('option', { value: i })));
}

// Pulls the file's current state. Returns false (and shows the passphrase form) when the session is gone.
async function refresh() {
  const r = await api('/api/derja/state');
  if (!r.ok) { show('login'); return false; }
  const n = r.data.count;
  $('#count').textContent = `${n} message${n === 1 ? '' : 's'} in the Excel file`;
  renderIntents(r.data.intents);
  renderRecent(r.data.recent);
  show('desk');
  return true;
}

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
  err.textContent = '';
  btn.disabled = true;
  const r = await api('/api/derja/add', {
    method: 'POST',
    body: { text: text.value.trim(), intent: $('#intent').value.trim(), script: $('#script').value },
  });
  btn.disabled = false;
  if (r.status === 401) {
    show('login');
    $('#login-err').textContent = 'Your session ended. Enter the passphrase again.';
    return;
  }
  if (!r.ok) { err.textContent = errText(r); return; }
  // The intent and script stay filled in, so labelling a run of similar messages is quick.
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
