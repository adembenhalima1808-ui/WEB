// The front door: "Initialize Neural Link", private-door riddles, owner sign-in, boot animation, offline screen.
import { $, api, h, errText, sleep } from './util.js';

const inner = () => $('#gate-inner');
const reactor = (icon, cls) => h('span', { class: 'reactor ' + cls, 'aria-hidden': 'true', text: icon });
function screen(...nodes) { const el = inner(); el.textContent = ''; el.className = 'gate-inner'; el.append(...nodes); void el.offsetWidth; }
function focusFirst() { const f = $('input', inner()); if (f) f.focus(); }

function form(fields, buttons, onSubmit, errBox) {
  const f = h('form', { autocomplete: 'off' }, ...fields);
  const row = h('div', { class: buttons.length > 1 ? 'gate-actions' : '' }, ...buttons);
  f.append(row, errBox);
  f.addEventListener('submit', async e => {
    e.preventDefault(); const sub = $('button[type=submit]', f); if (sub.disabled) return;
    sub.disabled = true; errBox.textContent = '';
    try { await onSubmit(); } finally { sub.disabled = false; }
  });
  return f;
}

export function createGate({ onEnter }) {
  // ---- 1. start
  async function enterWith(text, err, btn) {
    const restore = btn ? btn.textContent : null;
    if (btn) btn.textContent = 'Waking...';
    const r = await api('/api/gate', { method: 'POST', body: { text } });
    if (btn) btn.textContent = restore;
    if (r.status === 503) return showOffline(r.data.reason);
    if (!r.ok) { err.textContent = errText(r); return; }
    if (r.data.stage === 'admin') return showAdminPassword();
    if (r.data.stage === 'challenge') return showChallenge(r.data);
    await boot();
  }
  function showStart(note) {
    const err = h('p', { class: 'err', role: 'alert', text: note || '' });
    const input = h('input', { class: 'field', id: 'company', maxlength: '60', placeholder: 'e.g., Datadog, Hugging Face...', 'aria-label': 'Company name', autocomplete: 'off' });
    const btn = h('button', { class: 'btn primary', type: 'submit', text: 'Wake Agent' });
    const skip = h('a', { href: '#', class: 'gate-link', text: 'Skip to the CV', onclick: async e => {
      e.preventDefault(); if (skip.classList.contains('busy')) return;
      skip.classList.add('busy'); err.textContent = '';
      try { await enterWith('', err); } finally { skip.classList.remove('busy'); }
    } });
    const reportLink = h('a', { href: '/report', target: '_blank', rel: 'noopener', class: 'gate-link', text: 'How this agent was tested' });
    screen(reactor('\u{1F98A}', 'sleeping'), h('h2', { text: 'Initialize Neural Link' }),
      h('p', { class: 'muted', text: 'Tell the agent which company you are visiting from, or just wake it up.' }),
      form([input], [btn], () => enterWith(input.value, err, btn), err),
      h('div', { class: 'gate-links' }, skip, reportLink));
    focusFirst();
  }

  // ---- 2. boot animation for visitors
  async function boot() {
    const status = h('p', { class: 'muted fade-in', text: 'Bypassing security protocols...' });
    screen(reactor('\u{1F98A}', 'waking'), h('h2', { class: 'fade-in glow-accent', text: 'Authentication Accepted' }), status);
    await sleep(500);
    status.className = 'glow-green'; status.textContent = 'Neural Link Established. Booting Dashboard...';
    await sleep(1800);
    onEnter();
  }

  // ---- 3. private-door riddle (all wording comes from the server)
  function showChallenge(c) {
    const err = h('p', { class: 'err', role: 'alert' });
    const input = h('input', { class: 'field', type: 'password', maxlength: '120', 'aria-label': 'Your answer', placeholder: 'Your answer', autocomplete: 'off' });
    const ok = h('button', { class: 'btn primary', type: 'submit', text: c.button });
    const cancel = h('button', { class: 'btn', type: 'button', text: c.cancel, onclick: () => showStart() });
    screen(reactor(c.icon, c.theme === 'a' ? 'heart' : 'devil'), h('h2', { class: 'glow-accent', text: c.title }),
      h('p', { class: 'muted' }, c.prompt, h('br'), h('small', {}, h('i', { text: c.hint }))),
      form([input], [ok, cancel], async () => {
        const r = await api('/api/auth/family', { method: 'POST', body: { answer: input.value } });
        input.value = '';
        if (!r.ok) { err.textContent = errText(r); return; }
        document.body.classList.add('theme-' + r.data.theme);
        const line = h('p', { class: 'fade-in muted', text: r.data.lines[0] });
        screen(reactor(r.data.icon, r.data.theme === 'a' ? 'heart' : 'devil'), h('h2', { class: 'fade-in glow-accent', text: r.data.title }), line);
        await sleep(1200); line.textContent = r.data.lines[1]; line.className = 'glow-accent'; await sleep(2000);
        onEnter();
      }, err));
    focusFirst();
  }

  // ---- 4. owner sign-in: password, then a code sent to the owner's phone
  function showAdminPassword(inMaintenance) {
    const err = h('p', { class: 'err', role: 'alert' });
    const input = h('input', { class: 'field', type: 'password', maxlength: '200', 'aria-label': 'Owner password', placeholder: 'Owner password', autocomplete: 'current-password' });
    const ok = h('button', { class: 'btn primary', type: 'submit', text: 'Execute' });
    const cancel = h('button', { class: 'btn', type: 'button', text: 'Abort', onclick: () => (inMaintenance ? showOffline() : showStart()) });
    screen(reactor('\u{1F510}', 'waking'), h('h2', { class: 'glow-red', text: 'AUTHORIZATION REQUIRED' }),
      form([input], [ok, cancel], async () => {
        const r = await api('/api/auth/admin/start', { method: 'POST', body: { password: input.value } });
        input.value = '';
        if (!r.ok) { err.textContent = errText(r); return; }
        showOtp(inMaintenance);
      }, err));
    focusFirst();
  }
  function showOtp(inMaintenance) {
    const err = h('p', { class: 'err', role: 'alert' });
    const input = h('input', { class: 'field', type: 'password', inputmode: 'numeric', maxlength: '6', 'aria-label': '6-digit code', placeholder: '6-digit code', autocomplete: 'one-time-code' });
    const ok = h('button', { class: 'btn primary', type: 'submit', text: 'Verify Access' });
    const cancel = h('button', { class: 'btn', type: 'button', text: 'Abort', onclick: () => (inMaintenance ? showOffline() : showStart()) });
    screen(reactor('\u{1F510}', 'waking'), h('h2', { class: 'glow-red', text: 'ENTER YOUR CODE' }),
      h('p', { class: 'muted', text: 'A 6-digit code was sent to your phone.' }),
      form([input], [ok, cancel], async () => {
        const r = await api('/api/auth/admin/verify', { method: 'POST', body: { code: input.value } });
        input.value = '';
        if (!r.ok) { err.textContent = errText(r); return; }
        onEnter();
      }, err));
    focusFirst();
  }

  // ---- 5. maintenance screen (only the owner can get past it)
  function showOffline(reason) {
    const details = h('details', {}, h('summary', { text: 'Admin Access' }),
      h('p', { class: 'muted', text: 'Owner sign-in' }), h('button', { class: 'btn', type: 'button', text: 'Continue', onclick: () => showAdminPassword(true) }));
    screen(reactor('\u{1F98A}', 'sleeping'), h('h2', { class: 'glow-red', text: 'SYSTEM OFFLINE' }),
      h('p', { class: 'muted', text: reason || 'The system is under maintenance. Please check back shortly.' }), details);
  }

  return { showStart, showOffline };
}
