// Chat panel, direct comm-link and tool panels. All text via textContent / renderMd.
import { $, $$, api, h, errText, renderMd, stream, toast, downloadText, copyText } from './util.js';

function bubble(avatar, role, who) {
  const body = h('div', { class: 'body' });
  const m = h('div', { class: 'msg ' + role }, h('span', { class: 'av', 'aria-hidden': 'true', text: avatar }),
    h('div', {}, who ? h('span', { class: 'who', text: who }) : null, body));
  return { m, body };
}

/** Chat with suggested trails. send(text, history) -> {ok, reply|error}. */
export function createChat({ avatars, placeholder, prompts, greeting, saved = [], send, title, label = 'Message' }) {
  const [botAv, userAv] = avatars;
  const root = h('div');
  if (title) root.append(h('h3', { text: title }));
  const history = []; let busy = false;
  const trailsBox = h('div', { class: 'trails', role: 'group', 'aria-label': 'Suggested questions' });
  const log = h('div', { class: 'log', role: 'log', 'aria-live': 'polite', 'aria-label': 'Conversation', tabindex: '0' });
  const input = h('input', { class: 'field', id: 'chat-in-' + Math.random().toString(36).slice(2, 7), maxlength: '1500', placeholder, autocomplete: 'off', 'aria-label': label });
  const sendBtn = h('button', { class: 'btn primary auto', type: 'submit', text: 'Send' });
  const form = h('form', { class: 'composer' }, input, sendBtn);
  const scroll = () => { log.scrollTop = log.scrollHeight; };

  const add = (role, text, animate) => {
    const b = bubble(role === 'user' ? userAv : botAv, role); log.append(b.m);
    if (animate) return stream(b.body, text, scroll).then(scroll); renderMd(b.body, text); scroll(); return Promise.resolve();
  };
  saved.length ? saved.forEach(m => add(m.role === 'user' ? 'user' : 'assistant', m.content)) : add('assistant', greeting);

  const renderTrails = () => {
    trailsBox.textContent = '';
    prompts.forEach((p, i) => trailsBox.append(h('button', { class: 'btn', type: 'button', text: p, onclick: () => ask(p, i) })));
  };
  if (prompts && prompts.length) {
    root.append(h('p', { class: 'muted' }, h('strong', { text: 'Suggested trails to follow:' })), trailsBox); renderTrails();
  }

  async function ask(text, trailIdx) {
    text = (text || '').trim(); if (!text || busy) return;
    busy = true; sendBtn.disabled = true; $$('button', trailsBox).forEach(b => { b.disabled = true; });
    add('user', text); input.value = '';
    const typing = bubble(botAv, 'assistant'); typing.body.append(h('span', { class: 'typing', 'aria-label': 'Typing' }, h('i'), h('i'), h('i'))); log.append(typing.m); scroll();
    const r = await send(text, history.slice(-8));
    typing.m.remove();
    const reply = r.ok ? r.data.reply : errText(r);
    await add('assistant', reply, true);
    if (r.ok) history.push({ role: 'user', content: text }, { role: 'assistant', content: reply });
    busy = false; sendBtn.disabled = false; $$('button', trailsBox).forEach(b => { b.disabled = false; });
    if (r.ok && trailIdx != null) {
      const s = await api('/api/suggest', { method: 'POST', body: { user: text, bot: reply } });
      if (s.ok && s.data.suggestion) { prompts[trailIdx] = s.data.suggestion; renderTrails(); }
    }
  }
  form.addEventListener('submit', e => { e.preventDefault(); ask(input.value); });
  root.append(log, form);
  return {
    el: root,
    // Used by the operations tab: show the command and its output in the conversation too.
    note(userText, botText) { add('user', userText); add('assistant', botText); history.push({ role: 'user', content: userText }, { role: 'assistant', content: botText }); },
  };
}

/** Direct comm-link to the owner's phone. Polls only while its tab is visible. */
export function createComm({ avatar = '', refresh = 5, intro }) {
  const root = h('div');
  if (intro) root.append(h('p', { class: 'muted', text: intro }));
  const log = h('div', { class: 'log short', role: 'log', 'aria-live': 'polite', 'aria-label': 'Direct messages', tabindex: '0' });
  const empty = h('p', { class: 'empty', text: 'Comm-Link established. Awaiting input.' }); log.append(empty);
  const input = h('input', { class: 'field', maxlength: '1000', placeholder: 'Send a direct message to Adem...', autocomplete: 'off', 'aria-label': 'Direct message' });
  const form = h('form', { class: 'composer' }, input, h('button', { class: 'btn primary auto', type: 'submit', text: 'Send' }));
  root.append(log, form);
  let since = 0, timer = null; const seen = new Set();
  const render = m => {
    const key = m.unix_time + m.content; if (seen.has(key)) return; seen.add(key); empty.remove();
    const mine = m.role === 'user';
    const b = bubble(avatar, mine ? 'user' : 'assistant', `${mine ? (m.who || 'You') : 'Adem (Admin)'} · ${m.timestamp}`);
    b.body.textContent = m.content; log.append(b.m); since = Math.max(since, m.unix_time); log.scrollTop = log.scrollHeight;
  };
  const poll = async () => { const r = await api('/api/comm/messages?since=' + since); if (r.ok) r.data.messages.forEach(render); };
  form.addEventListener('submit', async e => {
    e.preventDefault(); const text = input.value.trim(); if (!text) return; input.value = '';
    const r = await api('/api/comm/send', { method: 'POST', body: { message: text } });
    if (!r.ok) toast(errText(r)); else poll();
  });
  return {
    el: root,
    start() { if (timer) return; poll(); timer = setInterval(() => { if (!document.hidden) poll(); }, Math.max(3, refresh) * 1000); },
    stop() { clearInterval(timer); timer = null; },
  };
}

/** Public "Agentic Operations": job description in, fit score / cover letter / interview questions out. */
export function createOps({ chat }) {
  const root = h('div');
  root.append(h('h3', { text: 'Agentic Operations' }), h('p', { class: 'muted', text: 'Inject a Job Description below to run autonomous candidate evaluations.' }));
  const jd = h('textarea', { class: 'textarea', id: 'jd', rows: '8', placeholder: 'Paste the full job description here...', 'aria-label': 'Target job description' });
  const err = h('p', { class: 'err', role: 'alert' });
  const out = h('div', { class: 'hide' });
  const actions = [['fit', 'Calculate Fit Score'], ['cover', 'Draft Cover Letter'], ['questions', 'Extract Interview Qs']];
  let busy = false;
  const btns = actions.map(([id, label]) => h('button', { class: 'btn', type: 'button', text: label, onclick: () => run(id, label) }));
  async function run(id, label) {
    if (busy) return; err.textContent = '';
    if (!jd.value.trim()) { err.textContent = 'Please paste a Job Description first.'; jd.classList.add('error'); jd.focus(); return; }
    jd.classList.remove('error'); busy = true; btns.forEach(b => { b.disabled = true; });
    out.className = 'output'; out.textContent = ''; out.append(h('p', { class: 'muted', text: `Executing agentic protocol: ${label}...` }));
    const r = await api('/api/agent', { method: 'POST', body: { action: id, jd: jd.value } });
    busy = false; btns.forEach(b => { b.disabled = false; });
    if (!r.ok) { out.className = 'hide'; err.textContent = errText(r); return; }
    const text = r.data.output, title = r.data.title;
    out.textContent = ''; const body = h('div', { class: 'body' });
    out.append(h('h4', { text: `${title} Output:` }), body); await stream(body, text);
    const row = h('div', { class: 'row' }, h('button', { class: 'btn', type: 'button', text: 'Copy', onclick: () => copyText(text).then(() => toast('Copied'), () => toast('Copy failed')) }));
    if (id === 'cover') row.append(h('button', { class: 'btn', type: 'button', text: 'Download Cover Letter (TXT)', onclick: () => downloadText('Cover_Letter_Adem_Ben_Halima.txt', text) }));
    out.append(row);
    chat.note(`System Command Executed: ${title} based on the provided Job Description.`, text);
  }
  root.append(jd, h('div', { class: 'row' }, ...btns), err, out);
  return { el: root };
}

/** Private-area tools (settle an argument, roast, ...). Spec comes from the server. */
export function createTools({ title, tools }) {
  const root = h('div'); root.append(h('h3', { text: title }));
  tools.forEach((t, idx) => {
    if (idx) root.append(h('hr', { class: 'divider' }));
    root.append(h('h4', { text: t.heading }));
    let input = null;
    if (t.input) {
      input = t.input === 'area' ? h('textarea', { class: 'textarea', rows: '4', maxlength: '800', 'aria-label': t.placeholder, placeholder: t.placeholder })
        : h('input', { class: 'field', maxlength: '800', 'aria-label': t.placeholder, placeholder: t.placeholder });
      root.append(input);
    }
    const err = h('p', { class: 'err', role: 'alert' }); const out = h('div', { class: 'hide' });
    const btn = h('button', { class: 'btn', type: 'button', text: t.label, onclick: async () => {
      err.textContent = '';
      if (input && !input.value.trim()) { err.textContent = 'Please write something first.'; input.focus(); return; }
      btn.disabled = true; out.className = 'output'; out.textContent = ''; out.append(h('p', { class: 'muted', text: 'Working on it...' }));
      const r = await api('/api/family/tool', { method: 'POST', body: { tool: t.id, text: input ? input.value : '' } });
      btn.disabled = false;
      if (!r.ok) { out.className = 'hide'; err.textContent = errText(r); return; }
      out.textContent = ''; const body = h('div', { class: 'body' }); out.append(h('h4', { text: t.result }), body); await stream(body, r.data.output);
    } });
    root.append(h('div', { class: 'row' }, btn), err, out);
  });
  return { el: root };
}
