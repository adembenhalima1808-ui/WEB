// Owner console. Every endpoint it calls is server-checked for the admin role.
import { $, api, h, errText, toast, readFile, downloadText } from './util.js';
import { makeTabs } from './tabs.js';

const guard = r => { if (r.status === 401 || r.status === 403) { toast('Session ended. Sign in again.'); setTimeout(() => location.reload(), 900); return false; } return true; };
const msg = (box, r, okText) => { box.className = r.ok ? 'err ok' : 'err'; box.textContent = r.ok ? okText : errText(r); };

export function buildAdmin() {
  const tabs = makeTabs(['Telemetry & Wiretap', 'Telegram Diagnostics', 'Agentic Training Simulator', 'Profile Sync', 'CMS & Identity', 'Projects', 'Recommendations', 'Private Area 1', 'Private Area 2', 'Vector Brain Injection']);
  telemetry(tabs.panels[0]); telegramPanel(tabs.panels[1]); simulator(tabs.panels[2]); profileSync(tabs.panels[3]); cms(tabs.panels[4]); projectsPanel(tabs.panels[5]); testimonialsPanel(tabs.panels[6]); private1Panel(tabs.panels[7]); private2Panel(tabs.panels[8]); brain(tabs.panels[9]);
  return h('div', {}, tabs.list, ...tabs.panels);
}

function telemetry(root) {
  const stats = h('div', { class: 'stat-grid' }), pills = h('div', { class: 'pills' }), rooms = h('div'), logs = h('div'), env = h('div', { class: 'pills' });
  const refresh = h('button', { class: 'btn auto', type: 'button', text: 'Refresh Logs', onclick: load });
  root.append(stats, h('h4', { text: 'Systems' }), env, h('h4', { text: 'Scanned Corporate Entities' }), pills, h('hr'),
    h('h4', { text: 'Live Comm-Link Rooms' }), rooms, h('hr'), h('div', { class: 'row' }, h('h4', { text: 'Live Chat Wiretap Logs (AI Bot)' }), refresh), logs);
  async function load() {
    const r = await api('/api/admin/overview'); if (!guard(r) || !r.ok) return;
    const a = r.data.analytics; stats.textContent = '';
    [['total_visits', 'Total Visits'], ['messages_sent', 'Bot Interactions'], ['cv_downloads', 'CVs Downloaded'], ['cover_letters_generated', 'Cover Letters']]
      .forEach(([k, l]) => stats.append(h('div', { class: 'stat' }, h('b', { text: String(a[k] || 0) }), h('span', { text: l }))));
    env.textContent = '';
    [['telegram', 'Telegram'], ['mistral', 'Mistral'], ['mistral_medium', 'Mistral (heavy)'], ['private1_enabled', 'Private area 1'], ['private2_enabled', 'Private area 2']]
      .forEach(([k, l]) => env.append(h('span', { class: 'pill', text: `${r.data.env[k] ? '✅' : '❌'} ${l}` })));
    pills.textContent = ''; (a.companies_logged || []).slice(-80).forEach(c => pills.append(h('span', { class: 'pill', text: String(c) })));
    if (!pills.children.length) pills.append(h('span', { class: 'muted', text: 'No specific company queries logged yet.' }));
    rooms.textContent = '';
    r.data.live_rooms.forEach(rm => rooms.append(h('details', { class: 'acc' }, h('summary', { text: `${rm.company || 'Visitor'} · ${rm.vid.slice(0, 8)} (${(rm.messages || []).length} messages)` }),
      h('div', { class: 'inner' }, (rm.messages || []).map(m => h('div', { class: 'logitem' }, h('div', { class: 't', text: m.timestamp || '' }), h('b', { class: 'u', text: m.role === 'user' ? 'Visitor: ' : 'You: ' }), m.content))))));
    if (!rooms.children.length) rooms.append(h('p', { class: 'muted', text: 'No open rooms.' }));
    logs.textContent = '';
    const groups = new Map(); r.data.chat_logs.forEach(l => { const k = l.company || 'Unknown Entity'; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(l); });
    groups.forEach((items, comp) => logs.append(h('details', { class: 'acc' }, h('summary', { text: `Intercepted: ${comp} (${items.length} messages)` }),
      h('div', { class: 'inner' }, items.map(l => h('div', { class: 'logitem' }, h('div', { class: 't', text: l.timestamp }),
        h('div', {}, h('b', { class: 'u', text: 'User: ' }), l.user), h('div', {}, h('b', { text: 'Agent: ' }), l.bot)))))));
    if (!groups.size) logs.append(h('p', { class: 'muted', text: 'No conversations intercepted yet.' }));
  }
  load();
}

function telegramPanel(root) {
  const out = h('p', { class: 'err', role: 'status' });
  root.append(h('h3', { text: 'Telegram Connection Diagnostics & Repair' }), h('div', { class: 'row' },
    h('div', {}, h('h4', { text: 'Test Telegram Alert Delivery' }), h('button', { class: 'btn', type: 'button', text: 'Send Test Alert Message', onclick: async () => {
      const r = await api('/api/admin/telegram/test', { method: 'POST' }); if (!guard(r)) return;
      out.className = r.ok && r.data.delivered ? 'err ok' : 'err'; out.textContent = r.ok && r.data.delivered ? 'SUCCESS: Telegram accepted the message.' : 'FAILURE: Telegram did not accept the message. Check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.'; } })),
    h('div', {}, h('h4', { text: 'Clear Stuck Webhooks' }), h('button', { class: 'btn', type: 'button', text: 'Force Clear Webhooks', onclick: async () => {
      const r = await api('/api/admin/telegram/clear', { method: 'POST' }); if (!guard(r)) return;
      out.className = r.ok && r.data.cleared ? 'err ok' : 'err'; out.textContent = r.ok && r.data.cleared ? 'Webhook purged. Reply polling is unblocked.' : 'Could not clear the webhook (token missing or rejected).'; } }))), out);
}

function simulator(root) {
  const role = h('input', { class: 'field', value: 'Recruiter at Hugging Face', maxlength: '120', 'aria-label': 'Target company and role' });
  const log = h('div', { class: 'log short', role: 'log', 'aria-live': 'polite', tabindex: '0' });
  const evalOut = h('div', { class: 'output hide' }); const prompt = h('textarea', { class: 'textarea hide', rows: '10', 'aria-label': 'Suggested master prompt' });
  const apply = h('button', { class: 'btn primary hide', type: 'button', text: 'Implement Advised Prompt' }); const err = h('p', { class: 'err', role: 'alert' });
  let chat = []; const busy = on => $('button', root) && root.querySelectorAll('button').forEach(b => { b.disabled = on; });
  async function turn() {
    err.textContent = ''; busy(true);
    const r = await api('/api/admin/sim/turn', { method: 'POST', body: { role: role.value, chat } }); busy(false);
    if (!guard(r)) return false; if (!r.ok) { err.textContent = errText(r); return false; }
    r.data.messages.forEach(m => { chat.push(m); const b = h('div', { class: 'msg' }, h('span', { class: 'av', 'aria-hidden': 'true', text: m.role === 'Recruiter' ? '\u{1F9D1}‍\u{1F4BC}' : '\u{1F98A}' }), h('div', {}, h('span', { class: 'who', text: m.role }), m.content)); log.append(b); });
    log.scrollTop = log.scrollHeight; return true;
  }
  root.append(h('h3', { text: 'Agentic Training Simulator' }), h('p', { class: 'muted', text: 'A simulated interviewer questions the agent, then a judge critiques the master prompt.' }), role,
    h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: 'Run 1 turn', onclick: turn }),
      h('button', { class: 'btn', type: 'button', text: 'Run 3 turns', onclick: async () => { for (let i = 0; i < 3; i++) if (!(await turn())) break; } }),
      h('button', { class: 'btn', type: 'button', text: 'Evaluate', onclick: async () => {
        err.textContent = ''; busy(true);
        const r = await api('/api/admin/sim/evaluate', { method: 'POST', body: { role: role.value, chat } }); busy(false);
        if (!guard(r)) return; if (!r.ok) { err.textContent = errText(r); return; }
        evalOut.className = 'output'; evalOut.textContent = ''; evalOut.append(h('h4', { text: 'Evaluation' }), h('div', { class: 'body', text: r.data.evaluation }));
        const sug = r.data.suggested_prompt || ''; prompt.value = sug; prompt.classList.toggle('hide', !sug); apply.classList.toggle('hide', !sug);
      } }),
      h('button', { class: 'btn', type: 'button', text: 'Reset', onclick: () => { chat = []; log.textContent = ''; evalOut.className = 'output hide'; prompt.classList.add('hide'); apply.classList.add('hide'); } })),
    h('h4', { text: 'Interview Simulation Log' }), log, evalOut, prompt, apply, err);
  apply.addEventListener('click', async () => { const r = await api('/api/admin/sim/apply', { method: 'POST', body: { prompt: prompt.value } }); if (guard(r)) toast(r.ok ? 'Persona updated' : errText(r)); });
}

const FIELDS = [
  ['title', 'Main Hero Title'], ['sidebar_subtitle', 'Sidebar Subtitle'], ['role_title', 'Hero Role Title'], ['location', 'Location'],
  ['status_text', 'Availability Status'], ['status_color', 'Status Pulse Color', 'color'], ['email', 'Email'],
  ['linkedin_url', 'LinkedIn URL (https)'], ['github_url', 'GitHub URL (https)'], ['refresh_rate', 'Comm-Link auto-refresh (seconds)', 'number'],
  ['intro_text', 'Hero Introduction Text', 'area'], ['human_comm_enabled', 'Enable Human Comm-Link Tab', 'bool'],
  ['skills_enabled', 'Show skills (sidebar badges + competencies radar)', 'bool'],
  ['skills_manual', 'Use my skills below instead of the AI-generated ones', 'bool'],
  ['projects_enabled', 'Show the Projects section (public repos from the GitHub URL above)', 'bool'],
  ['testimonials_enabled', 'Show the "What people say" recommendations section', 'bool'],
  ['projects_repos', 'Fallback when the Projects tab has no cards: your repos to list, comma-separated (empty = 6 most recent)', 'area'],
  ['skills_stack', 'Skill badges (comma-separated)', 'area'], ['skills_radar', 'Radar skills, one "Name: score 0-100" per line (3-10 lines)', 'area'],
  ['persona_prompt', 'Master Persona Prompt', 'area'], ['maintenance_mode', 'Enable Maintenance Mode (locks out everyone but you)', 'bool'],
  ['maintenance_reason', 'Maintenance Notice Message', 'area'],
];
function cms(root) {
  const form = h('div', { class: 'cfg' }); const out = h('p', { class: 'err', role: 'status' });
  root.append(h('h3', { text: 'CMS & Identity' }), form);
  api('/api/admin/config').then(r => {
    if (!guard(r) || !r.ok) return;
    FIELDS.forEach(([k, label, type]) => {
      const id = 'cfg-' + k, v = r.data[k];
      if (type === 'bool') { const c = h('input', { type: 'checkbox', id }); c.checked = !!v; form.append(h('div', { class: 'check' }, c, h('label', { for: id, text: label }))); return; }
      const el = type === 'area' ? h('textarea', { class: 'textarea', id, rows: k.endsWith('prompt') ? '8' : '3' })
        : h('input', { class: type === 'color' ? '' : 'field', id, type: type === 'number' ? 'number' : type === 'color' ? 'color' : 'text', min: type === 'number' ? '2' : null, max: type === 'number' ? '60' : null });
      el.value = v == null ? '' : v;
      form.append(h('div', { class: type === 'area' ? 'wide' : '' }, h('label', { for: id, text: label }), el));
    });
  });
  root.append(h('button', { class: 'btn primary', type: 'button', text: 'Inject Overrides', onclick: async () => {
    const body = {}; FIELDS.forEach(([k,, t]) => { const el = document.getElementById('cfg-' + k); if (el) body[k] = t === 'bool' ? el.checked : el.value; });
    const r = await api('/api/admin/config', { method: 'POST', body }); if (guard(r)) msg(out, r, 'Saved. Invalid values (bad colour, non-https link, bad email) are ignored.');
  } }), out, h('hr'));
  root.append(h('p', { class: 'hint', text: 'To replace the CV or let the AI rewrite this text from it, use the Profile Sync tab.' }), h('hr'), h('div', { class: 'row' },
    h('button', { class: 'btn', type: 'button', text: 'Force Clear Neural Cache', onclick: async () => { const r = await api('/api/admin/clear-cache', { method: 'POST' }); if (guard(r)) toast(r.ok ? 'Application memory cache cleared.' : errText(r)); } })));
}

// One persona-prompt field, saved through the same /api/admin/config endpoint as CMS & Identity (partial updates only touch the key sent).
function personaField(root, key, label) {
  const area = h('textarea', { class: 'textarea', rows: '10', 'aria-label': label });
  const out = h('p', { class: 'err', role: 'status' });
  api('/api/admin/config').then(r => { if (guard(r) && r.ok) area.value = r.data[key] || ''; });
  root.append(h('h4', { text: label }), area,
    h('button', { class: 'btn primary', type: 'button', text: 'Save persona prompt', onclick: async () => {
      const r = await api('/api/admin/config', { method: 'POST', body: { [key]: area.value } }); if (guard(r)) msg(out, r, 'Saved.');
    } }), out, h('hr'));
}

function private1Panel(root) {
  personaField(root, 'private1_persona_prompt', 'Private Area 1 persona prompt');
  root.append(h('button', { class: 'btn danger', type: 'button', text: 'Wipe private chat history', onclick: async () => {
    if (!confirm('Permanently erase the private chat history?')) return;
    const r = await api('/api/admin/wipe-history', { method: 'POST' }); if (guard(r)) toast(r.ok ? 'History wiped.' : errText(r));
  } }), h('hr'));

  // ---- quotes: things Adem said, each stamped with when
  const qList = h('div', { class: 'drafts' }), qOut = h('p', { class: 'err', role: 'status' });
  function qBox(q) {
    const text = h('textarea', { class: 'textarea', rows: '2', 'data-k': 'text', 'aria-label': 'Quote text' }); text.value = q.text || '';
    const date = h('input', { class: 'field', 'data-k': 'date', placeholder: 'DD/MM', maxlength: '10', 'aria-label': 'Date' }); date.value = q.date || '';
    const time = h('input', { class: 'field', 'data-k': 'time', placeholder: 'HH:MM', maxlength: '10', 'aria-label': 'Time' }); time.value = q.time || '';
    const b = h('div', { class: 'draft' },
      h('div', { class: 'cfg' }, h('div', { class: 'wide' }, h('label', { class: 'lbl', text: 'Quote' }), text),
        h('div', {}, h('label', { class: 'lbl', text: 'Date' }), date), h('div', {}, h('label', { class: 'lbl', text: 'Time' }), time)),
      h('div', { class: 'row' },
        h('button', { class: 'btn', type: 'button', text: '↑ Up', onclick: () => { const s = b.previousElementSibling; if (s) s.before(b); } }),
        h('button', { class: 'btn', type: 'button', text: '↓ Down', onclick: () => { const s = b.nextElementSibling; if (s) s.after(b); } }),
        h('button', { class: 'btn danger', type: 'button', text: 'Remove', onclick: () => b.remove() })));
    return b;
  }
  const readQ = b => { const o = {}; b.querySelectorAll('[data-k]').forEach(el => { o[el.dataset.k] = el.value.trim(); }); return o; };
  const qSummary = h('span', { text: 'See all quotes to edit' });
  const renderQ = items => { qList.replaceChildren(...items.map(qBox)); qSummary.textContent = `See all ${items.length} quote${items.length === 1 ? '' : 's'} to edit`; };
  root.append(h('h3', { text: 'Quotes' }), h('p', { class: 'hint', text: 'Things Adem said, shown as a scrolling strip on this private area’s page with when they were said.' }),
    h('details', { class: 'acc' }, h('summary', {}, qSummary), h('div', { class: 'inner' }, qList)),
    h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: '+ Add quote', onclick: () => { qList.append(qBox({})); qList.closest('details').open = true; } }),
      h('button', { class: 'btn primary', type: 'button', text: 'Save quotes', onclick: async () => {
        const r = await api('/api/admin/private1/quotes', { method: 'POST', body: { quotes: [...qList.children].map(readQ) } }); if (!guard(r)) return;
        msg(qOut, r, 'Saved.'); if (r.ok) renderQ(r.data.quotes);
      } })), qOut, h('hr'));
  api('/api/admin/private1/quotes').then(r => { if (guard(r) && r.ok) renderQ(r.data.quotes); });

  // ---- photo timeline
  const pFile = h('input', { class: 'field', type: 'file', accept: 'image/jpeg,image/png,image/webp', 'aria-label': 'Select a photo' });
  const pOut = h('p', { class: 'err', role: 'status' }), pList = h('div', { class: 'drafts' });
  function pBox(p) {
    const img = h('img', { src: `/api/private1/photo/${p.id}`, alt: '', loading: 'lazy', style: 'width:100%;max-height:200px;object-fit:cover;border-radius:6px' });
    const caption = h('textarea', { class: 'textarea', rows: '2', 'data-k': 'caption', 'aria-label': 'Caption' }); caption.value = p.caption || '';
    const date = h('input', { class: 'field', 'data-k': 'date', placeholder: 'e.g. Paris, June 2026', 'aria-label': 'Date / place' }); date.value = p.date || '';
    const b = h('div', { class: 'draft', 'data-id': p.id }, img,
      h('div', { class: 'cfg' }, h('div', { class: 'wide' }, h('label', { class: 'lbl', text: 'Caption' }), caption),
        h('div', { class: 'wide' }, h('label', { class: 'lbl', text: 'Date / place' }), date)),
      h('div', { class: 'row' },
        h('button', { class: 'btn', type: 'button', text: '↑ Earlier', onclick: () => { const s = b.previousElementSibling; if (s) s.before(b); } }),
        h('button', { class: 'btn', type: 'button', text: '↓ Later', onclick: () => { const s = b.nextElementSibling; if (s) s.after(b); } }),
        h('button', { class: 'btn danger', type: 'button', text: 'Remove', onclick: () => b.remove() })));
    return b;
  }
  const readP = b => ({ id: b.dataset.id, caption: b.querySelector('[data-k="caption"]').value.trim(), date: b.querySelector('[data-k="date"]').value.trim() });
  const renderP = items => pList.replaceChildren(...items.map(pBox));
  const upload = h('button', { class: 'btn', type: 'button', text: 'Upload photo', onclick: async () => {
    const f = pFile.files[0]; if (!f) { pOut.className = 'err'; pOut.textContent = 'Choose a photo first.'; return; }
    const data = await readFile(f, true);
    const r = await api('/api/admin/private1/photos/upload', { method: 'POST', body: { image_b64: String(data).split(',')[1] || '' } });
    if (!guard(r)) return; if (!r.ok) { msg(pOut, r); return; }
    pList.append(pBox({ id: r.data.id, caption: '', date: '' })); pOut.className = 'err ok'; pOut.textContent = 'Uploaded. Add a caption/date below, in timeline order, then save.'; pFile.value = '';
  } });
  root.append(h('h3', { text: 'Timeline photos' }),
    h('p', { class: 'hint', text: 'Shown as a photo timeline on this private area’s page, oldest first. Upload, caption, order with Earlier/Later, then save.' }),
    pFile, upload, h('hr'), pList, h('div', { class: 'row' },
      h('button', { class: 'btn primary', type: 'button', text: 'Save timeline', onclick: async () => {
        const r = await api('/api/admin/private1/photos', { method: 'POST', body: { photos: [...pList.children].map(readP) } }); if (!guard(r)) return;
        msg(pOut, r, 'Saved.'); if (r.ok) renderP(r.data.photos);
      } })), pOut);
  api('/api/admin/private1/photos').then(r => { if (guard(r) && r.ok) renderP(r.data.photos); });
}

function private2Panel(root) {
  personaField(root, 'private2_persona_prompt', 'Private Area 2 persona prompt');
}

function brain(root) {
  const out = h('p', { class: 'err', role: 'status' }); const area = h('textarea', { class: 'textarea brain', rows: '16', 'aria-label': 'Live brain contents' });
  const file = h('input', { class: 'field', type: 'file', accept: '.txt,text/plain', 'aria-label': 'Select a .txt file to append' });
  const reload = () => api('/api/admin/brain').then(r => { if (guard(r) && r.ok) area.value = r.data.text; });
  root.append(h('h3', { text: 'Bulk Vector Upload' }), file, h('button', { class: 'btn', type: 'button', text: 'Inject File Knowledge', onclick: async () => {
    const f = file.files[0]; if (!f) { out.className = 'err'; out.textContent = 'Choose a .txt file first.'; return; }
    const r = await api('/api/admin/brain/append', { method: 'POST', body: { text: await readFile(f, false) } }); if (!guard(r)) return; msg(out, r, 'Knowledge fused!'); if (r.ok) reload();
  } }), h('hr'), h('h3', { text: 'Direct Memory Editor' }), area,
  h('button', { class: 'btn primary', type: 'button', text: 'Overwrite Neural Core', onclick: async () => { const r = await api('/api/admin/brain', { method: 'POST', body: { text: area.value } }); if (guard(r)) msg(out, r, 'Core overwritten! Memory rebuilds on the next question.'); } }), out);
  reload();
}

const DRAFT_LABELS = [['sidebar_subtitle', 'Sidebar Subtitle'], ['role_title', 'Hero Role Title'], ['location', 'Location'],
  ['status_text', 'Availability Status'], ['intro_text', 'Hero Introduction Text'], ['profile_block', 'Chatbot brain: PROFILE section']];

// Upload a new CV (YAML and/or PDF), then let the AI draft the site text. Nothing AI-written goes live until Apply.
function profileSync(root) {
  const state = h('div', { class: 'pills' });
  const loadStatus = () => api('/api/admin/profile').then(r => {
    if (!guard(r) || !r.ok) return; const d = r.data; state.replaceChildren(
      h('span', { class: 'pill', text: `Chatbot reads: ${d.chat_source === 'pdf' ? 'uploaded PDF' : 'YAML (' + d.yaml_source + ')'}` }),
      h('span', { class: 'pill', text: `Visitors download: ${d.custom_pdf ? 'your uploaded PDF' : 'PDF built from the YAML'}` }),
      h('span', { class: 'pill', text: `Last CV update: ${d.updated || 'never'}` }));
    state._yaml = d.yaml_text; resetPdf.hidden = !d.custom_pdf;
  });

  // 1. YAML: check first, then publish
  const yFile = h('input', { class: 'field', type: 'file', accept: '.yaml,.yml,text/yaml', 'aria-label': 'Select resume YAML' });
  const yOut = h('p', { class: 'err', role: 'status' }), yPrev = h('div');
  let yText = '';
  const publish = h('button', { class: 'btn primary', type: 'button', text: 'Publish this CV to the site', hidden: true, onclick: async () => {
    publish.disabled = true; const r = await api('/api/admin/profile/yaml', { method: 'POST', body: { yaml: yText, publish: true } }); publish.disabled = false;
    if (!guard(r)) return; msg(yOut, r, 'Published. The chatbot, skills chart and CV download now use this CV. Next: generate the site text below.');
    if (r.ok) { publish.hidden = true; yPrev.replaceChildren(); loadStatus(); }
  } });
  const check = h('button', { class: 'btn', type: 'button', text: 'Check file', onclick: async () => {
    const f = yFile.files[0]; if (!f) { yOut.className = 'err'; yOut.textContent = 'Choose a .yaml file first.'; return; }
    yText = await readFile(f, false); publish.hidden = true; yPrev.replaceChildren();
    const r = await api('/api/admin/profile/yaml', { method: 'POST', body: { yaml: yText } }); if (!guard(r)) return;
    if (!r.ok) { msg(yOut, r); return; }
    const p = r.data.preview, c = p.counts;
    yOut.className = 'err ok'; yOut.textContent = `Looks good: ${p.name} · ${c.experience} experience, ${c.projects} projects, ${c.education} education, ${c.skill_groups} skill groups, ${c.languages} languages. Review, then publish.`;
    yPrev.replaceChildren(h('details', { class: 'acc' }, h('summary', { text: 'What the chatbot will read' }), h('pre', { class: 'inner preview', text: p.text })));
    publish.hidden = false;
  } });
  const yDownload = h('button', { class: 'btn', type: 'button', text: 'Download current YAML', onclick: () => state._yaml ? downloadText('resume.yaml', state._yaml) : toast('No YAML on the server yet.') });

  // 2. PDF for download (optionally also the chatbot's source)
  const pFile = h('input', { class: 'field', type: 'file', accept: 'application/pdf', 'aria-label': 'Select CV PDF' });
  const forChat = h('input', { type: 'checkbox', id: 'pdf-chat' }), pOut = h('p', { class: 'err', role: 'status' });
  const resetPdf = h('button', { class: 'btn', type: 'button', text: 'Go back to the PDF built from the YAML', hidden: true, onclick: async () => {
    const r = await api('/api/admin/resume/reset', { method: 'POST' }); if (guard(r)) { msg(pOut, r, 'Visitors now download the PDF built from the YAML.'); loadStatus(); }
  } });
  const pUpload = h('button', { class: 'btn', type: 'button', text: 'Upload PDF', onclick: async () => {
    const f = pFile.files[0]; if (!f) { pOut.className = 'err'; pOut.textContent = 'Choose a PDF first.'; return; }
    const data = await readFile(f, true);
    const r = await api('/api/admin/resume', { method: 'POST', body: { pdf_b64: String(data).split(',')[1] || '', use_for_chat: forChat.checked } });
    if (!guard(r)) return; msg(pOut, r, forChat.checked ? 'PDF published for download, and the chatbot now reads it.' : 'PDF published. Visitors download it; the chatbot keeps reading the YAML.'); loadStatus();
  } });

  // 3. AI drafts, reviewed field by field
  const dOut = h('p', { class: 'err', role: 'status' }), drafts = h('div', { class: 'drafts' });
  const apply = h('button', { class: 'btn primary', type: 'button', text: 'Apply checked changes to the live site', hidden: true, onclick: async () => {
    const body = {}; drafts.querySelectorAll('.draft').forEach(d => { if (d._use.checked) body[d._key] = d._area.value; });
    if (!Object.keys(body).length) { dOut.className = 'err'; dOut.textContent = 'Tick at least one change to apply.'; return; }
    const r = await api('/api/admin/profile/apply', { method: 'POST', body }); if (!guard(r)) return;
    msg(dOut, r, 'Live! Reload the public page to see it.'); if (r.ok) { drafts.replaceChildren(); apply.hidden = true; }
  } });
  const gen = h('button', { class: 'btn', type: 'button', text: 'Generate drafts with AI', onclick: async () => {
    gen.disabled = true; dOut.className = 'err ok'; dOut.textContent = 'Reading your CV and drafting… (about 10–20 seconds)';
    const r = await api('/api/admin/profile/draft', { method: 'POST' }); gen.disabled = false; if (!guard(r)) return;
    if (!r.ok) { msg(dOut, r); return; }
    dOut.className = 'err ok'; dOut.textContent = 'Drafts ready. Nothing is live yet: check each one, edit if needed, untick what you want to keep as is.';
    const { current, proposed } = r.data;
    drafts.replaceChildren(...DRAFT_LABELS.map(([k, label]) => {
      const same = (proposed[k] || '') === (current[k] || ''), id = 'draft-' + k;
      const use = h('input', { type: 'checkbox', id }); use.checked = !!proposed[k] && !same;
      const area = h('textarea', { class: 'textarea', rows: k === 'profile_block' ? '9' : k === 'intro_text' ? '4' : '2', 'aria-label': `New ${label}` });
      area.value = proposed[k] || ''; area.addEventListener('input', () => { use.checked = true; });
      const d = h('div', { class: 'draft' }, h('div', { class: 'check' }, use, h('label', { for: id, text: `${label}${same ? ' (no change)' : ''}` })),
        h('p', { class: 'was' }, h('b', { text: 'Now: ' }), current[k] || '(empty)'), area);
      d._key = k; d._use = use; d._area = area; return d;
    }));
    apply.hidden = false;
  } });

  root.append(h('h3', { text: 'Profile Sync' }), state, h('hr'),
    h('h4', { text: '1. CV data (resume.yaml)' }), h('p', { class: 'hint', text: 'Feeds the chatbot, the skills chart and the auto-built PDF. Checked before anything changes.' }),
    yFile, h('div', { class: 'row' }, check, yDownload), yOut, yPrev, publish, h('hr'),
    h('h4', { text: '2. CV PDF for download (optional)' }), h('p', { class: 'hint', text: 'Use this for a nicer designed CV (e.g. FlowCV). Without it, visitors get the PDF built from the YAML.' }),
    pFile, h('div', { class: 'check' }, forChat, h('label', { for: 'pdf-chat', text: 'The chatbot should read this PDF instead of the YAML' })),
    h('div', { class: 'row' }, pUpload, resetPdf), pOut, h('hr'),
    h('h4', { text: '3. Rewrite the site text with AI' }), h('p', { class: 'hint', text: 'The AI drafts from the CV above. You review every line; nothing goes live until you apply it.' }),
    gen, dOut, drafts, apply);
  loadStatus();
}

// Project cards. Empty fields fall back to the repo's GitHub data (name, description, topics, website).
const CARD_FIELDS = [
  ['repo', 'GitHub repo (owner/name), any public repo, including shared ones'], ['title', 'Title (empty = repo name)'],
  ['role', 'Role line, e.g. "Team of 5 · My part: ..."', 'wide'], ['tagline', 'Pitch, 1-2 sentences (empty = GitHub description)', 'area'],
  ['highlights', 'Key numbers, one "value | label" per line (max 3)', 'area'], ['tech', 'Tech badges, comma-separated (empty = GitHub topics)'],
  ['image', 'Cover image path, e.g. /static/projects/name.jpg (16:9)'], ['link', 'Extra button link (https://... or /path)'], ['link_label', 'Extra button label'],
];
function projectsPanel(root) {
  const list = h('div', { class: 'drafts' }), out = h('p', { class: 'err', role: 'status' });
  const toForm = c => ({ ...c, highlights: (c.highlights || []).map(x => `${x.value} | ${x.label}`).join('\n'), tech: (c.tech || []).join(', ') });
  const fromForm = box => {
    const v = k => box.querySelector(`[data-k="${k}"]`).value.trim();
    return { repo: v('repo'), title: v('title'), role: v('role'), tagline: v('tagline'), image: v('image'), link: v('link'), link_label: v('link_label'),
      highlights: v('highlights').split('\n').map(l => l.split('|')).filter(x => x[0].trim()).map(([a, ...b]) => ({ value: a.trim(), label: b.join('|').trim() })),
      tech: v('tech').split(',').map(t => t.trim()).filter(Boolean) };
  };
  function cardBox(c) {
    const f = toForm(c), form = h('div', { class: 'cfg' }), box = h('div', { class: 'draft' });
    CARD_FIELDS.forEach(([k, label, type]) => {
      const el = type === 'area' ? h('textarea', { class: 'textarea', rows: '3', 'data-k': k, 'aria-label': label }) : h('input', { class: 'field', 'data-k': k, 'aria-label': label });
      el.value = f[k] || ''; form.append(h('div', { class: type ? 'wide' : '' }, h('label', { class: 'lbl', text: label }), el));
    });
    const move = d => { const sib = d < 0 ? box.previousElementSibling : box.nextElementSibling; if (sib) d < 0 ? sib.before(box) : sib.after(box); };
    box.append(h('h4', { text: c.title || c.repo || 'New project' }), form, h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: '\u2191 Up', onclick: () => move(-1) }),
      h('button', { class: 'btn', type: 'button', text: '\u2193 Down', onclick: () => move(1) }),
      h('button', { class: 'btn danger', type: 'button', text: 'Remove', onclick: () => box.remove() })));
    return box;
  }
  const render = cards => list.replaceChildren(...cards.map(cardBox));
  root.append(h('h3', { text: 'Projects' }),
    h('p', { class: 'hint', text: 'Cards shown on the public page, in this order. Links, language, stars and dates come from GitHub automatically (refreshed hourly). With no cards, the page lists your own public repos instead.' }),
    list, h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: '+ Add project', onclick: () => list.append(cardBox({})) }),
      h('button', { class: 'btn primary', type: 'button', text: 'Save projects', onclick: async () => {
        const r = await api('/api/admin/projects', { method: 'POST', body: { cards: [...list.children].map(fromForm) } }); if (!guard(r)) return;
        msg(out, r, 'Saved. Reload the public page to see it. Invalid repo names, images or links were dropped.'); if (r.ok) render(r.data.cards);
      } })), out);
  api('/api/admin/projects').then(r => { if (guard(r) && r.ok) render(r.data.cards); });
}

// Recommendations. The chatbot quotes these word for word, so paste them exactly as written.
const REC_FIELDS = [
  ['name', 'Name'], ['title', 'Their title, e.g. "Manager, GoMyCode Sousse"'], ['relation', 'How they know you, e.g. "Managed Adem directly"', 'wide'],
  ['date', 'Date, e.g. "September 2026"'], ['linkedin_url', 'LinkedIn link where it can be checked (empty = none)'],
  ['highlight', 'Lead sentence shown in large type (copy it exactly from the text)', 'area'], ['text', 'Full text, exactly as written (blank line between paragraphs)', 'area'],
];
function testimonialsPanel(root) {
  const list = h('div', { class: 'drafts' }), out = h('p', { class: 'err', role: 'status' });
  function box(t) {
    const form = h('div', { class: 'cfg' }), b = h('div', { class: 'draft' });
    REC_FIELDS.forEach(([k, label, type]) => {
      const el = type === 'area' ? h('textarea', { class: 'textarea', rows: k === 'text' ? '7' : '2', 'data-k': k, 'aria-label': label }) : h('input', { class: 'field', 'data-k': k, 'aria-label': label });
      el.value = t[k] || ''; form.append(h('div', { class: type ? 'wide' : '' }, h('label', { class: 'lbl', text: label }), el));
    });
    const letter = h('input', { type: 'checkbox', 'data-k': 'letter' }); letter.checked = !!t.letter;
    form.append(h('div', { class: 'check wide' }, letter, h('label', { text: 'I also have a signed letter from them (shows a "Request the signed letter" button)' })));
    const move = d => { const sib = d < 0 ? b.previousElementSibling : b.nextElementSibling; if (sib) d < 0 ? sib.before(b) : sib.after(b); };
    b.append(h('h4', { text: t.name || 'New recommendation' }), form, h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: '\u2191 Up', onclick: () => move(-1) }),
      h('button', { class: 'btn', type: 'button', text: '\u2193 Down', onclick: () => move(1) }),
      h('button', { class: 'btn danger', type: 'button', text: 'Remove', onclick: () => b.remove() })));
    return b;
  }
  const read = b => { const o = {}; b.querySelectorAll('[data-k]').forEach(el => { o[el.dataset.k] = el.type === 'checkbox' ? el.checked : el.value.trim(); }); return o; };
  const render = items => list.replaceChildren(...items.map(box));
  root.append(h('h3', { text: 'Recommendations' }),
    h('p', { class: 'hint', text: 'Shown as "What people say" on the public page, and quoted word for word by the chatbot. Only add people who agreed to be named.' }),
    list, h('div', { class: 'row' },
      h('button', { class: 'btn', type: 'button', text: '+ Add recommendation', onclick: () => list.append(box({})) }),
      h('button', { class: 'btn primary', type: 'button', text: 'Save recommendations', onclick: async () => {
        const r = await api('/api/admin/testimonials', { method: 'POST', body: { testimonials: [...list.children].map(read) } }); if (!guard(r)) return;
        msg(out, r, 'Saved. The page and the chatbot use them right away. Entries without a name or text were dropped.'); if (r.ok) render(r.data.testimonials);
      } })), out);
  api('/api/admin/testimonials').then(r => { if (guard(r) && r.ok) render(r.data.testimonials); });
}
