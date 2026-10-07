// The dashboard shell: sidebar + main card. One layout for visitors, owner and private areas.
import { $, api, h, errText, toast, reduced } from './util.js';
import { drawRadar } from './radar.js';
import { makeTabs } from './tabs.js';
import { createChat, createComm, createOps, createTools } from './chat.js';
import { buildAdmin } from './admin.js';
import { projectCard } from './project-card.js';
import { renderTimeline, renderQuoteMarquee } from './timeline.js';

// How many project cards the homepage shows before linking out to /projects,
// so the page stays short no matter how many projects get added later.
const FEATURED_PROJECTS = 2;

const NS = 'http://www.w3.org/2000/svg';
const ICONS = {
  linkedin: 'M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z',
  email: 'M0 3v18h24v-18h-24zm21.518 2l-9.518 7.713-9.518-7.713h19.036zm-19.518 14v-11.817l10 8.104 10-8.104v11.817h-20z',
  github: 'M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z',
};
function icon(path) {
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('aria-hidden', 'true');
  const p = document.createElementNS(NS, 'path'); p.setAttribute('d', path); svg.append(p); return svg;
}
const greetingWord = () => { const hr = new Date().getHours(); return hr < 12 ? 'Good morning' : hr < 18 ? 'Good afternoon' : 'Good evening'; };
const hexToRgb = hex => /^#[0-9a-fA-F]{6}$/.test(hex) ? [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)).join(', ') : '255, 122, 0';

function sidebar({ kind, cfg, ui }) {
  const aside = $('#sidebar'); aside.textContent = '';
  const showCv = kind !== 'private', showSkills = showCv && cfg.skills_enabled !== false;
  aside.append(h('h2', { text: 'Adem Ben Halima' }));
  if (kind === 'private') {
    aside.append(h('p', { class: 'caption', text: ui.caption }), h('div', { class: 'status theme-' + ui.theme },
      h('div', { class: 'status-row' }, h('span', { class: 'pulse', 'aria-hidden': 'true' }), h('span', { class: 'status-text', text: ui.badge })),
      h('div', { class: 'status-sub', text: '\u{1F4CD} ' + ui.badge_sub })));
  } else if (kind === 'admin') {
    aside.append(h('p', { class: 'caption', text: cfg.sidebar_subtitle }), h('div', { class: 'status root' },
      h('div', { class: 'status-row' }, h('span', { class: 'pulse', 'aria-hidden': 'true' }), h('span', { class: 'status-text', text: 'ROOT ACCESS ACTIVE' })),
      h('div', { class: 'status-sub', text: '\u{1F4CD} ' + (cfg.location || '') })));
  } else {
    aside.append(h('p', { class: 'caption', text: cfg.sidebar_subtitle }), h('div', { class: 'status' },
      h('div', { class: 'status-row' }, h('span', { class: 'pulse', 'aria-hidden': 'true' }), h('span', { class: 'status-text', text: cfg.status_text })),
      h('div', { class: 'status-sub', text: '\u{1F4CD} ' + (cfg.location || '') })));
  }
  let badges = null;
  if (showCv) {
    aside.append(h('a', { class: 'btn', href: '/api/cv', download: '', text: 'Download Full CV' }),
      h('a', { class: 'btn', href: '/report', target: '_blank', rel: 'noopener', text: 'How This Agent Was Tested' }));
  }
  if (showSkills) {
    aside.append(h('hr'), h('h3', { text: 'My Skills' }));
    badges = h('div', { class: 'badges', 'aria-live': 'polite' }, h('span', { class: 'badge', text: 'Loading...' })); aside.append(badges);
  }
  if (kind !== 'private') {
    aside.append(h('hr'));
    const socials = h('div', { class: 'socials' });
    if (cfg.linkedin_url) socials.append(h('a', { class: 'social', href: cfg.linkedin_url, target: '_blank', rel: 'noopener noreferrer', 'aria-label': 'LinkedIn', title: 'LinkedIn' }, icon(ICONS.linkedin)));
    if (cfg.github_url) socials.append(h('a', { class: 'social', href: cfg.github_url, target: '_blank', rel: 'noopener noreferrer', 'aria-label': 'GitHub', title: 'GitHub' }, icon(ICONS.github)));
    if (cfg.email) socials.append(h('a', { class: 'social', href: 'mailto:' + cfg.email, 'aria-label': 'Email ' + cfg.email, title: cfg.email }, icon(ICONS.email)));
    aside.append(socials, h('hr'));

    const fbText = h('textarea', { class: 'textarea', rows: '4', maxlength: '1000', 'aria-label': 'Suggestions, bugs, or thoughts?', placeholder: 'Suggestions, bugs, or thoughts?' });
    const fbMsg = h('p', { class: 'err', role: 'status' });
    const fb = h('form', {}, fbText, h('button', { class: 'btn', type: 'submit', text: 'Send Anonymously' }), fbMsg);
    fb.addEventListener('submit', async e => {
      e.preventDefault(); if (!fbText.value.trim()) return;
      const r = await api('/api/feedback', { method: 'POST', body: { text: fbText.value } });
      fbMsg.className = r.ok ? 'err ok' : 'err'; fbMsg.textContent = r.ok ? 'Feedback sent!' : errText(r); if (r.ok) fbText.value = '';
    });
    aside.append(h('details', {}, h('summary', { text: 'Leave Feedback' }), fb));
  } else {
    aside.append(h('hr'));
  }
  aside.append(h('button', { class: 'btn', type: 'button', text: 'Terminate Connection', onclick: async () => { await api('/api/end', { method: 'POST' }); location.reload(); } }));
  return badges;
}

async function loadSkills(badges, radarBox) {
  const r = await api('/api/skills');
  if (!r.ok) {
    if (r.data.enabled === false) { badges?.previousElementSibling?.remove(); badges?.remove(); radarBox?.previousElementSibling?.remove(); radarBox?.remove(); return; }
  if (badges) { badges.textContent = ''; badges.append(h('span', { class: 'badge', text: 'Unavailable' })); }
    if (radarBox) { radarBox.textContent = ''; radarBox.append(h('p', { class: 'loading', text: r.status === 503 ? 'Competencies are offline during maintenance.' : 'Competencies are unavailable right now.' })); }
    return;
  }
  if (badges) { badges.textContent = ''; (r.data.stack || []).forEach(t => badges.append(h('span', { class: 'badge', text: t }))); }
  if (radarBox) drawRadar(radarBox, r.data.categories, r.data.scores);
}

// Project cards: owner-written text merged with live GitHub data. The whole section disappears when there is nothing to show.
// Only the first FEATURED_PROJECTS show here; the rest stay one click away on /projects so the homepage doesn't grow forever.
async function loadProjects(section, grid) {
  const r = await api('/api/projects');
  const list = r.ok ? r.data.projects || [] : [];
  if (!list.length) { section.remove(); return; }
  grid.replaceChildren(...list.slice(0, FEATURED_PROJECTS).map(projectCard));
  // Always linked, not just once there's overflow: with <= FEATURED_PROJECTS cards /projects
  // would otherwise have no way in from the UI at all.
  const label = list.length > FEATURED_PROJECTS ? `View all ${list.length} projects \u2192` : 'All projects \u2192';
  section.append(h('div', { class: 'projects-more' }, h('a', { class: 'btn', href: '/projects', text: label })));
}

// Recommendations: the strongest sentence up front, the full text one click away, and where each one can be checked.
const initials = n => n.split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('');
function quoteCard(t, email) {
  const paras = t.text.split(/\n\s*\n/).map(p => h('p', { text: p }));
  const mail = email ? `mailto:${email}?subject=${encodeURIComponent('Recommendation letter from ' + t.name)}` : null;
  return h('article', { class: 'quote' },
    h('span', { class: 'quote-mark', 'aria-hidden': 'true', text: '\u201C' }),
    h('blockquote', {}, h('p', { class: 'quote-lead', text: t.highlight || t.text.split(/(?<=\.)\s/)[0] })),
    h('details', { class: 'quote-full' }, h('summary', { text: 'Read the full recommendation' }), h('div', {}, paras)),
    h('div', { class: 'quote-who' },
      h('span', { class: 'quote-avatar', 'aria-hidden': 'true', text: initials(t.name) }),
      h('div', {}, h('b', { text: t.name }), h('span', { text: t.title }), h('span', { class: 'muted', text: [t.relation, t.date].filter(Boolean).join(' \u00B7 ') }))),
    h('div', { class: 'quote-src' },
      t.letter ? h('span', { class: 'badge', text: '\u2709 Signed letter' }) : null,
      t.linkedin_url ? h('a', { class: 'badge', href: t.linkedin_url, target: '_blank', rel: 'noopener noreferrer', text: 'On LinkedIn \u2197' }) : null,
      t.letter && mail ? h('a', { class: 'btn', href: mail, text: 'Request the signed letter' }) : null));
}
async function loadTestimonials(section, grid, email) {
  const r = await api('/api/testimonials');
  const list = r.ok ? r.data.testimonials || [] : [];
  if (!list.length) { section.remove(); return; }
  grid.replaceChildren(...list.map(t => quoteCard(t, email)));
}

// Section header: small label with a rule, title, one-line subtitle. Gives every block on the page the same rhythm.
const sectionHead = (label, title, sub) => h('header', { class: 'section-head' },
  h('span', { class: 'section-label', text: label }), h('h3', { text: title }), sub ? h('p', { text: sub }) : null);

function wireMenu() {
  const app = $('#app'), btn = $('#menu-btn');
  const set = open => { app.classList.toggle('open', open); btn.setAttribute('aria-expanded', String(open)); btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu'); };
  btn.onclick = () => set(!app.classList.contains('open'));
  $('#scrim').onclick = () => set(false);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
}

export async function buildApp({ role, cfg, me }) {
  $('#app').classList.remove('hide'); wireMenu();
  const main = $('#main'); main.textContent = '';
  const refresh = Number(cfg.refresh_rate) || 5;
  const color = cfg.status_color;
  if (/^#[0-9a-fA-F]{6}$/.test(color)) { document.documentElement.style.setProperty('--status', color); document.documentElement.style.setProperty('--status-rgb', hexToRgb(color)); }

  // ------- owner console
  if (role === 'admin') {
    document.title = 'Command Center';
    const badges = sidebar({ kind: 'admin', cfg });
    main.append(h('h1', { text: 'ROOT COMMAND CENTER' }));
    main.append(buildAdmin());
    if (badges) loadSkills(badges, null);
    return;
  }

  // ------- private areas (copy, colours and tools all come from the server)
  if (role) {
    const r = await api('/api/family/state');
    if (!r.ok) { location.reload(); return; }
    const ui = r.data; document.title = ui.title; document.body.classList.add('theme-' + ui.theme);
    sidebar({ kind: 'private', cfg, ui });
    main.append(h('h1', { text: ui.title }), h('p', { class: 'meta' }, h('b', { text: 'Role:' }), ` ${ui.role_line} | `, h('b', { text: 'Location:' }), ` ${ui.location}`), h('p', { text: ui.intro }));
    if ('photos' in ui) {
      if (ui.quotes && ui.quotes.length) { const qb = h('div'); main.append(qb, h('hr')); renderQuoteMarquee(qb, ui.quotes); }
      main.append(h('h3', { text: 'Our Timeline' }));
      const tb = h('div'); main.append(tb, h('hr')); renderTimeline(tb, ui.photos || []);
    } else {
      main.append(h('h3', { text: ui.radar_title }));
      const rb = h('div', { class: 'radar-wrap' }); main.append(rb, h('hr'));
      drawRadar(rb, ui.radar.categories, ui.radar.scores);
    }
    const comm = cfg.human_comm_enabled ? createComm({ avatar: ui.avatars[0], refresh }) : null;
    const labels = comm ? ui.tabs : ui.tabs.slice(0, 2);
    const tabs = makeTabs(labels, { onChange: i => { if (comm) (i === 2 ? comm.start() : comm.stop()); } });
    const chat = createChat({
      avatars: ui.avatars, placeholder: ui.placeholder, prompts: ui.prompts.slice(), greeting: ui.greeting, saved: ui.history || [], title: ui.chat_title,
      send: (text, hist) => api('/api/family/chat', { method: 'POST', body: { message: text, history: hist } }),
    });
    tabs.panels[0].append(chat.el);
    tabs.panels[1].append(createTools({ title: ui.tools_title, tools: ui.tools }).el);
    if (comm) tabs.panels[2].append(h('h3', { text: 'Direct Comm-Link' }), comm.el);
    main.append(tabs.list, ...tabs.panels.slice(0, labels.length));
    return;
  }

  // ------- public visitor
  document.title = `${cfg.title} | ${cfg.role_title}`;
  const badges = sidebar({ kind: 'public', cfg });
  main.append(h('h1', { text: cfg.title }),
    h('p', { class: 'meta' }, h('b', { text: 'Role:' }), ` ${cfg.role_title} | `, h('b', { text: 'Location:' }), ` ${cfg.location}`),
    h('p', { text: cfg.intro_text }));
  const showSkills = cfg.skills_enabled !== false;
  if (showSkills) {
    const rb = h('div', { class: 'radar-wrap', 'aria-live': 'polite' }, h('p', { class: 'loading', text: 'Agent extracting core competencies from CV...' }));
    main.append(sectionHead('Skills', 'Core Engineering Competencies', me.company ? `Weighted for ${me.company}.` : null), rb);
    loadSkills(badges, rb);
  }
  if (cfg.projects_enabled !== false) {
    const grid = h('div', { class: 'projects', 'aria-live': 'polite' }, h('p', { class: 'loading', text: 'Fetching projects from GitHub...' }));
    const section = h('section', { 'aria-label': 'Projects' }, sectionHead('Work', 'Projects', 'What I built, with the code on GitHub.'), grid);
    main.append(section);
    loadProjects(section, grid);
  }
  if (cfg.testimonials_enabled !== false) {
    const grid = h('div', { class: 'quotes', 'aria-live': 'polite' });
    const section = h('section', { 'aria-label': 'Recommendations' }, sectionHead('References', 'What people say', "From managers I've worked with."), grid);
    main.append(section);
    loadTestimonials(section, grid, cfg.email);
  }

  const comm = cfg.human_comm_enabled ? createComm({ avatar: '\u{1F9D1}‍\u{1F4BB}', refresh, intro: 'Bypass the AI and send a message directly to my personal device. I will reply here if available.' }) : null;
  const labels = ['Direct Interrogation', 'Agentic Operations'].concat(comm ? ['Direct Comm-Link'] : []);
  const tabs = makeTabs(labels, { onChange: i => { if (comm) (i === 2 ? comm.start() : comm.stop()); } });
  const ctxLine = me.company ? `Context locked to ${me.company}.` : 'General tracking initialized.';
  const greeting = `${greetingWord()}. I am the Kitsune Agent, Adem's autonomous digital twin. \u{1F98A} ${ctxLine}\n\n` +
    'Welcome to the Command Center. Here is your tactical breakdown:\n\n' +
    (showSkills ? "- **The Radar Web (above):** a live view of Adem's core engineering competencies, re-weighted for your company.\n" : '') +
    (cfg.projects_enabled !== false ? "- **Projects (above):** what Adem has built, with the code on GitHub.\n" : '') +
    (cfg.testimonials_enabled !== false ? '- **What people say (above):** recommendations from managers Adem has worked with.\n' : '') +
    "- **Direct Interrogation (here):** ask me anything about Adem's experience, projects or how he solves problems.\n" +
    '- **Agentic Operations (next tab):** feed me a job description and I will calculate a fit score, draft a cover letter or generate interview questions.\n' +
    (comm ? "- **Direct Comm-Link (3rd tab):** bypass the AI and ping Adem's phone in real time.\n" : '') +
    '- **Feedback (sidebar):** found a bug or have a suggestion? Leave an anonymous note.\n\nHow can I assist you today?';
  const chat = createChat({
    avatars: ['\u{1F98A}', '\u{1F9D1}‍\u{1F4BB}'], placeholder: 'Input query here...', greeting, title: 'Direct Interrogation Interface',
    prompts: ['What are your core AI skills?', 'What architectures have you built?', 'Why should we hire you?'],
    send: (text, hist) => api('/api/chat', { method: 'POST', body: { message: text, history: hist } }),
  });
  tabs.panels[0].append(chat.el);
  tabs.panels[1].append(createOps({ chat }).el);
  if (comm) tabs.panels[2].append(h('h3', { text: 'Direct Comm-Link' }), comm.el);
  main.append(sectionHead('Talk to the agent', 'Ask me anything', 'Answers come only from my CV and notes. You can also paste a job description.'), tabs.list, ...tabs.panels);
}
