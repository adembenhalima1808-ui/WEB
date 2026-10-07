// Private area 1's page: a photo timeline (Adem adds photos from the owner console, this
// private area's own visitor can add her own too) and a scrolling strip of things Adem has
// said, each stamped with when he said it.
import { h, api, errText, readFile } from './util.js';

function timelineCard(p, i) {
  const img = h('img', { src: `/api/private1/photo/${p.id}`, alt: p.caption || '', loading: 'lazy' });
  const card = h('div', { class: 'timeline-card' }, img, (p.caption || p.date) ?
    h('div', { class: 'timeline-body' },
      p.caption ? h('p', { class: 'timeline-caption', text: p.caption }) : null,
      p.date ? h('span', { class: 'timeline-date', text: p.date }) : null) : null);
  return h('div', { class: 'timeline-item ' + (i % 2 ? 'right' : 'left') }, h('span', { class: 'timeline-dot', 'aria-hidden': 'true' }), card);
}

function observeReveal(line) {
  if (!('IntersectionObserver' in window)) { line.querySelectorAll('.timeline-item').forEach(el => el.classList.add('in-view')); return; }
  const io = new IntersectionObserver(entries => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in-view'); io.unobserve(e.target); } }), { threshold: 0.2 });
  line.querySelectorAll('.timeline-item').forEach(el => io.observe(el));
}

export function renderTimeline(container, photos) {
  const empty = h('p', { class: 'muted', text: 'No photos yet — add the first one below.' });
  const line = h('div', { class: 'timeline' });
  const renderList = items => {
    line.replaceChildren(...items.map(timelineCard));
    empty.hidden = items.length > 0;
    observeReveal(line);
  };
  renderList(photos);

  const file = h('input', { class: 'field', type: 'file', accept: 'image/jpeg,image/png,image/webp', 'aria-label': 'Choose a picture to add' });
  const caption = h('input', { class: 'field', maxlength: '400', placeholder: 'A little caption (optional)', 'aria-label': 'Caption' });
  const date = h('input', { class: 'field', maxlength: '40', placeholder: 'e.g. Paris, June 2026 (optional)', 'aria-label': 'Date / place' });
  const out = h('p', { class: 'err', role: 'status' });
  const add = h('button', { class: 'btn primary', type: 'button', text: 'Add to our timeline', onclick: async () => {
    const f = file.files[0]; if (!f) { out.className = 'err'; out.textContent = 'Choose a picture first.'; return; }
    add.disabled = true; out.className = 'err'; out.textContent = '';
    const data = await readFile(f, true);
    const r = await api('/api/private1/photos', { method: 'POST', body: { image_b64: String(data).split(',')[1] || '', caption: caption.value, date: date.value } });
    add.disabled = false;
    if (!r.ok) { out.textContent = errText(r); return; }
    renderList(r.data.photos); out.className = 'err ok'; out.textContent = 'Added!';
    file.value = ''; caption.value = ''; date.value = '';
  } });

  container.append(empty, line, h('div', { class: 'timeline-add' },
    h('p', { class: 'timeline-add-label', text: 'Add your own picture' }), file, caption, date, add, out));
}

export function renderQuoteMarquee(container, quotes) {
  if (!quotes.length) return;
  const chip = q => h('div', { class: 'quote-chip' },
    h('span', { class: 'quote-mark', 'aria-hidden': 'true', text: '“' }),
    h('p', { text: q.text }),
    (q.date || q.time) ? h('span', { class: 'quote-stamp', text: [q.date, q.time].filter(Boolean).join(' · ') }) : null);
  const track = h('div', { class: 'quote-track' }, ...quotes.map(chip), ...quotes.map(chip));
  container.append(h('div', { class: 'quote-marquee' }, track));
}
