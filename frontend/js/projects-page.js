// Standalone /projects page: every card, no featured-N cutoff (that's the homepage's job).
import { api, h } from './util.js';
import { projectCard } from './project-card.js';

const grid = document.getElementById('grid');
const r = await api('/api/projects');
const list = r.ok ? r.data.projects || [] : [];
grid.replaceChildren(...(list.length ? list.map(projectCard) : [h('p', { class: 'loading', text: 'No projects to show right now.' })]));
