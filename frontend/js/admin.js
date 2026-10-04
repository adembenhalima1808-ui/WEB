// Owner console. Every endpoint it calls is server-checked for the admin role.
import { $, api, h, errText, toast, readFile, downloadText } from './util.js';
import { makeTabs } from './tabs.js';

const guard = r => { if (r.status === 401 || r.status === 403) { toast('Session ended. Sign in again.'); setTimeout(() => location.reload(), 900); return false; } return true; };
const msg = (box, r, okText) => { box.className = r.ok ? 'err ok' : 'err'; box.textContent = r.ok ? okText : errText(r); };

export function buildAdmin() {
  const tabs = makeTabs(['Telemetry & Wiretap', 'Telegram Diagnostics', 'Agentic Training Simulator', 'Profile Sync', 'CMS & Identity', 'Vector Brain Injection']);
  telemetry(tabs.panels[0]); telegramPanel(tabs.panels[1]); simulator(tabs.panels[2]); profileSync(tabs.panels[3]); cms(tabs.panels[4]); brain(tabs.panels[5]);
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
  ['skills_stack', 'Skill badges (comma-separated)', 'area'], ['skills_radar', 'Radar skills, one "Name: score 0-100" per line (3-10 lines)', 'area'],
  ['persona_prompt', 'Master Persona Prompt', 'area'], ['private1_persona_prompt', 'Private area 1 persona prompt', 'area'],
  ['private2_persona_prompt', 'Private area 2 persona prompt', 'area'], ['maintenance_mode', 'Enable Maintenance Mode (locks out everyone but you)', 'bool'],
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
    h('button', { class: 'btn', type: 'button', text: 'Force Clear Neural Cache', onclick: async () => { const r = await api('/api/admin/clear-cache', { method: 'POST' }); if (guard(r)) toast(r.ok ? 'Application memory cache cleared.' : errText(r)); } }),
    h('button', { class: 'btn danger', type: 'button', text: 'Wipe private chat history', onclick: async () => { if (!confirm('Permanently erase the private chat history?')) return; const r = await api('/api/admin/wipe-history', { method: 'POST' }); if (guard(r)) toast(r.ok ? 'History wiped.' : errText(r)); } })));
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
