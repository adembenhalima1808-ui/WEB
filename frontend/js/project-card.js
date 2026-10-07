// Project card rendering, shared by the homepage preview (shell.js) and the
// full /projects page, so the two never drift apart.
import { h } from './util.js';

const NS = 'http://www.w3.org/2000/svg';
const GITHUB_PATH = 'M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z';

function githubIcon() {
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('aria-hidden', 'true');
  const p = document.createElementNS(NS, 'path'); p.setAttribute('d', GITHUB_PATH); svg.append(p); return svg;
}

const monthYear = d => { const t = new Date(d); return isNaN(t) ? '' : t.toLocaleDateString('en', { month: 'short', year: 'numeric' }); };

export function projectCard(p) {
  const main = p.url || p.link || null, ext = u => /^https:/.test(u) ? { target: '_blank', rel: 'noopener noreferrer' } : {};
  const meta = [p.stars ? `★ ${p.stars}` : '', p.pushed ? `Updated ${monthYear(p.pushed)}` : ''].filter(Boolean).join(' · ');
  return h('article', { class: 'project' },
    p.image ? h('a', { class: 'project-cover', href: main, tabindex: '-1', 'aria-hidden': 'true', ...ext(main || '') },
      h('img', { src: p.image, alt: '', loading: 'lazy', width: '960', height: '540' }),
      p.language ? h('span', { class: 'project-lang', text: p.language }) : null) : null,
    h('div', { class: 'project-body' },
      p.role ? h('p', { class: 'project-role', text: p.role }) : null,
      h('h4', {}, main ? h('a', { href: main, text: p.title, ...ext(main) }) : p.title),
      p.tagline ? h('p', { class: 'tagline', text: p.tagline }) : null,
      p.highlights.length ? h('div', { class: 'project-stats' }, p.highlights.map(x => h('div', {}, h('b', { text: x.value }), h('span', { text: x.label })))) : null,
      p.tech.length ? h('div', { class: 'badges' }, p.tech.map(t => h('span', { class: 'badge', text: t }))) : null,
      h('div', { class: 'project-foot' },
        meta || (!p.image && p.language) ? h('span', { class: 'meta-line', text: [!p.image ? p.language : '', meta].filter(Boolean).join(' · ') }) : null,
        p.url ? h('a', { class: 'btn', href: p.url, target: '_blank', rel: 'noopener noreferrer', 'aria-label': `${p.title} source code on GitHub` }, githubIcon(), 'Code') : null,
        p.link ? h('a', { class: 'btn primary', href: p.link, ...ext(p.link) }, p.link_label + (/^https:/.test(p.link) ? ' ↗' : '')) : null)));
}
