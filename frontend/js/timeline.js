// Private area 1's page: a "memory of the day" hero, a short preview of the photo timeline
// with a link into the full starry view, and a scrolling strip of things Adem has said, each
// stamped with when he said it.
// Also shared with private area 2: a reel of video drops, each a countdown until its reveal
// moment then a player - editable on one side (where they're dropped from), read-only on the other.
import { h, api, errText, toast, readFile } from './util.js';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
  'September', 'October', 'November', 'December'];

function formatMonth(iso) {
  const m = /^(\d{4})-(\d{2})$/.exec(iso || '');
  if (!m) return '';
  const n = Number(m[2]);
  return n >= 1 && n <= 12 ? `${MONTHS[n - 1]} ${m[1]}` : '';
}
function memoryLabel(p) {
  const bits = [p.place, formatMonth(p.date)].filter(Boolean);
  return bits.join(', ');
}

function wavePath(segments, height) {
  const step = height / segments;
  let d = 'M50,0';
  for (let i = 0; i < segments; i++) {
    const y0 = i * step, y1 = y0 + step, cx = i % 2 === 0 ? 78 : 22;
    d += ` C${cx},${y0 + step * 0.15} ${cx},${y1 - step * 0.15} 50,${y1}`;
  }
  return d;
}
const NS = 'http://www.w3.org/2000/svg';
function timelineWave(count) {
  const segments = Math.max(2, count);
  const H = segments * 100;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `0 0 100 ${H}`);
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.setAttribute('class', 'timeline-wave');
  svg.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(NS, 'path');
  path.setAttribute('d', wavePath(segments, H));
  path.setAttribute('fill', 'none');
  svg.append(path);
  return svg;
}

function timelineCard(p, i) {
  const img = h('img', { src: `/api/private1/photo/${p.id}`, alt: p.caption || '', loading: 'lazy' });
  const label = memoryLabel(p);
  const card = h('div', { class: 'timeline-card' }, img, (p.caption || label) ?
    h('div', { class: 'timeline-body' },
      p.caption ? h('p', { class: 'timeline-caption', text: p.caption }) : null,
      label ? h('span', { class: 'timeline-date', text: label }) : null) : null);
  return h('div', { class: 'timeline-item ' + (i % 2 ? 'right' : 'left') }, h('span', { class: 'timeline-dot', 'aria-hidden': 'true' }), card);
}

function observeReveal(line) {
  if (!('IntersectionObserver' in window)) { line.querySelectorAll('.timeline-item').forEach(el => el.classList.add('in-view')); return; }
  const io = new IntersectionObserver(entries => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in-view'); io.unobserve(e.target); } }), { threshold: 0.2 });
  line.querySelectorAll('.timeline-item').forEach(el => io.observe(el));
}

function buildLine(photos) {
  const line = h('div', { class: 'timeline' });
  if (!photos.length) { line.append(h('p', { class: 'muted', text: 'No photos yet — add the first one.' })); return line; }
  line.append(timelineWave(photos.length), ...photos.map(timelineCard));
  observeReveal(line);
  return line;
}

// A handful of shooting stars at a time, looping gently, only while the full view is open.
function startAmbientShower(host) {
  let stop = false;
  const spawn = () => {
    if (stop) return;
    const star = h('span', { class: 'shooting-star', 'aria-hidden': 'true' });
    star.style.setProperty('--star-top', (5 + Math.random() * 70) + '%');
    star.style.setProperty('--star-dy', (25 + Math.random() * 40) + 'vh');
    star.style.setProperty('--star-duration', (1.6 + Math.random() * 1) + 's');
    host.append(star);
    setTimeout(() => star.remove(), 3200);
  };
  const t = setInterval(spawn, 1500);
  spawn();
  return () => { stop = true; clearInterval(t); };
}

function openAddMemoryModal({ onSaved }) {
  const file = h('input', { class: 'field', type: 'file', accept: 'image/jpeg,image/png,image/webp', 'aria-label': 'Choose a picture to add' });
  const caption = h('input', { class: 'field', maxlength: '400', placeholder: 'A little caption (optional)', 'aria-label': 'Caption' });
  const place = h('input', { class: 'field', maxlength: '80', placeholder: 'Place (optional)', 'aria-label': 'Place' });
  const date = h('input', { class: 'field', type: 'month', 'aria-label': 'Month' });
  const out = h('p', { class: 'err', role: 'status' });
  const addBtn = h('button', { class: 'btn primary', type: 'button', text: 'Add to our timeline', onclick: async () => {
    const f = file.files[0]; if (!f) { out.className = 'err'; out.textContent = 'Choose a picture first.'; return; }
    addBtn.disabled = true; out.className = 'err'; out.textContent = '';
    const data = await readFile(f, true);
    const r = await api('/api/private1/photos', { method: 'POST', body: { image_b64: String(data).split(',')[1] || '', caption: caption.value, place: place.value, date: date.value } });
    addBtn.disabled = false;
    if (!r.ok) { out.textContent = errText(r); return; }
    close(); onSaved(r.data.photos);
  } });
  const overlay = h('div', { class: 'modal-overlay', onclick: e => { if (e.target === overlay) close(); } });
  const closeBtn = h('button', { class: 'modal-close', type: 'button', 'aria-label': 'Close', text: '×', onclick: () => close() });
  overlay.append(h('div', { class: 'modal-card', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Add a memory' },
    closeBtn, h('h3', { text: '✨ Add a Memory' }), file,
    h('div', { class: 'memory-fields' }, place, date), caption, addBtn, out));
  function onKey(e) { if (e.key === 'Escape') close(); }
  function close() { overlay.remove(); document.removeEventListener('keydown', onKey); }
  document.addEventListener('keydown', onKey);
  document.body.append(overlay);
  file.focus();
}

// The hero at the top of the page: a random memory, inviting a comment on it (which pings
// Adem's Telegram the same way a mood ping does, and a reply shows up in Direct Comm-Link).
export function renderMemoryOfDay(container, photos) {
  if (!photos.length) return;
  const p = photos[Math.floor(Math.random() * photos.length)];
  const label = memoryLabel(p);
  const text = h('input', { class: 'field', maxlength: '500', placeholder: 'Say something about this one...', 'aria-label': 'Comment on this memory' });
  const send = h('button', { class: 'btn primary auto', type: 'button', text: 'Send', onclick: async () => {
    const v = text.value.trim(); if (!v) return;
    send.disabled = true;
    const r = await api('/api/private1/memory-comment', { method: 'POST', body: { photo_id: p.id, text: v } });
    send.disabled = false;
    if (!r.ok) { toast(errText(r)); return; }
    text.value = ''; toast('Sent — he’ll see it.');
  } });
  const form = h('div', { class: 'motd-form' }, text, send);
  container.append(h('div', { class: 'motd' },
    h('span', { class: 'motd-eyebrow', text: '✨ A memory for today' }),
    h('div', { class: 'motd-body' },
      h('img', { src: `/api/private1/photo/${p.id}`, alt: p.caption || '', loading: 'lazy' }),
      h('div', { class: 'motd-text' },
        p.caption ? h('p', { class: 'motd-caption', text: p.caption }) : null,
        label ? h('span', { class: 'motd-date', text: label }) : null,
        form))));
}

// Returns { open() } so the sidebar's "Add a Memory" shortcut can trigger the same popup.
export function renderTimeline(container, photos) {
  let items = photos.slice();
  const PREVIEW = 3;
  const view = h('div');
  container.append(view);

  function showPreview() {
    view.replaceChildren();
    view.append(buildLine(items.slice(0, PREVIEW)));
    if (items.length > PREVIEW || items.length === 0) {
      view.append(h('div', { class: 'timeline-more' },
        h('button', { class: 'btn', type: 'button', text: `✨ See the full timeline (${items.length})`, onclick: showFull })));
    }
    view.append(h('div', { class: 'timeline-add' },
      h('button', { class: 'btn primary timeline-add-trigger', type: 'button', text: '✨ Add a Memory', onclick: openModal })));
  }

  function showFull() {
    view.replaceChildren();
    const sky = h('div', { class: 'timeline-sky', 'aria-hidden': 'true' });
    const stopShower = startAmbientShower(sky);
    const back = h('button', { class: 'btn', type: 'button', text: '← Back', onclick: () => { stopShower(); showPreview(); } });
    view.append(sky, back, buildLine(items),
      h('div', { class: 'timeline-add' },
        h('button', { class: 'btn primary timeline-add-trigger', type: 'button', text: '✨ Add a Memory', onclick: openModal })));
  }

  function openModal() {
    openAddMemoryModal({ onSaved: photos => { items = photos; (items.length > PREVIEW ? showFull : showPreview)(); } });
  }

  showPreview();
  return { open: openModal };
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

// ----- video drops: upload, caption, pick a reveal moment -----
// "reveal_at" travels as a naive "YYYY-MM-DDTHH:MM" string, matching <input type="datetime-local">
// and compared against the viewer's own clock here - same convention the server uses on its side.
const TARGET_FMT = { dateStyle: 'medium', timeStyle: 'short' };
function formatTarget(revealAt) {
  const d = new Date(revealAt);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleString(undefined, TARGET_FMT);
}
function nowLocalInput() {
  const d = new Date(Date.now() - new Date().getTimezoneOffset() * 60000);
  return d.toISOString().slice(0, 16);
}
function pad2(n) { return String(Math.max(0, n)).padStart(2, '0'); }

function videoCountdown(revealAt) {
  const seg = (label) => { const n = h('b', { text: '00' }); return [n, h('div', { class: 'count-seg' }, n, h('span', { text: label }))]; };
  const [dN, dEl] = seg('days'), [hN, hEl] = seg('hrs'), [mN, mEl] = seg('min'), [sN, sEl] = seg('sec');
  const wrap = h('div', { class: 'video-countdown' },
    h('span', { class: 'video-eyebrow', text: '\u{1F39E} Unlocks soon' }),
    h('div', { class: 'count-grid' }, dEl, hEl, mEl, sEl),
    h('span', { class: 'video-target', text: formatTarget(revealAt) }));
  function tick() {
    const diff = new Date(revealAt).getTime() - Date.now();
    const s = Math.max(0, Math.floor(diff / 1000));
    dN.textContent = pad2(Math.floor(s / 86400)); hN.textContent = pad2(Math.floor(s / 3600) % 24);
    mN.textContent = pad2(Math.floor(s / 60) % 60); sN.textContent = pad2(s % 60);
    return diff <= 0;
  }
  const done = tick();
  wrap._tick = tick;
  return { el: wrap, done };
}

function videoCard(v, { editable, onDelete }) {
  const del = editable ? h('button', { class: 'btn danger auto video-delete', type: 'button', text: 'Remove', onclick: async () => {
    if (!confirm('Delete this video for good?')) return;
    const r = await api('/api/private2/videos/delete', { method: 'POST', body: { id: v.id } });
    if (!r.ok) { toast(errText(r)); return; }
    onDelete(r.data.videos);
  } }) : null;
  const caption = v.caption ? h('p', { class: 'video-caption', text: v.caption }) : null;
  if (v.revealed) {
    const player = h('video', { class: 'video-player', controls: true, preload: 'metadata', playsinline: true },
      h('source', { src: `/api/family/video/${v.id}` }));
    return h('div', { class: 'video-card' }, player, caption, del);
  }
  const { el: countdown } = videoCountdown(v.reveal_at);
  return h('div', { class: 'video-card' }, countdown, caption, del);
}

function openAddVideoModal({ onSaved }) {
  const file = h('input', { class: 'field', type: 'file', accept: 'video/mp4,video/webm,video/quicktime', 'aria-label': 'Choose a video to add' });
  const caption = h('input', { class: 'field', maxlength: '300', placeholder: 'A little caption (optional)', 'aria-label': 'Caption' });
  const reveal = h('input', { class: 'field', type: 'datetime-local', min: nowLocalInput(), 'aria-label': 'When can we see it?' });
  const out = h('p', { class: 'err', role: 'status' });
  const addBtn = h('button', { class: 'btn primary', type: 'button', text: 'Schedule the reveal', onclick: async () => {
    const f = file.files[0]; if (!f) { out.className = 'err'; out.textContent = 'Choose a video first.'; return; }
    if (!reveal.value) { out.className = 'err'; out.textContent = 'Pick when we get to see it.'; return; }
    addBtn.disabled = true; out.className = 'err'; out.textContent = '';
    const data = await readFile(f, true);
    const r = await api('/api/private2/videos', { method: 'POST',
      body: { video_b64: String(data).split(',')[1] || '', caption: caption.value, reveal_at: new Date(reveal.value).toISOString() } });
    addBtn.disabled = false;
    if (!r.ok) { out.textContent = errText(r); return; }
    close(); onSaved(r.data.videos);
  } });
  const overlay = h('div', { class: 'modal-overlay', onclick: e => { if (e.target === overlay) close(); } });
  const closeBtn = h('button', { class: 'modal-close', type: 'button', 'aria-label': 'Close', text: '×', onclick: () => close() });
  overlay.append(h('div', { class: 'modal-card', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Add a video' },
    closeBtn, h('h3', { text: '\u{1F39E} Drop a video' }), file, caption,
    h('p', { class: 'hint', text: 'Pick a moment and it stays a countdown for both of you until then.' }), reveal,
    addBtn, out));
  function onKey(e) { if (e.key === 'Escape') close(); }
  function close() { overlay.remove(); document.removeEventListener('keydown', onKey); }
  document.addEventListener('keydown', onKey);
  document.body.append(overlay);
  file.focus();
}

export function renderVideoReel(container, videos, { editable = false } = {}) {
  let items = videos.slice();
  let ticker = null;
  const view = h('div');
  container.append(view);

  function render() {
    clearInterval(ticker);
    view.replaceChildren();
    if (items.length) {
      const grid = h('div', { class: 'video-grid' }, ...items.map(v => videoCard(v, { editable, onDelete: setItems })));
      view.append(grid);
      ticker = setInterval(() => {
        let someDone = false;
        grid.querySelectorAll('.video-countdown').forEach(el => { if (el._tick && el._tick()) someDone = true; });
        if (someDone) refresh();
      }, 1000);
    } else {
      view.append(h('p', { class: 'muted', text: editable ? 'No videos yet — drop the first one.' : 'Nothing dropped yet.' }));
    }
    if (editable) {
      view.append(h('div', { class: 'timeline-add' },
        h('button', { class: 'btn primary timeline-add-trigger', type: 'button', text: '\u{1F39E} Add a Video', onclick: openModal })));
    }
  }
  function setItems(next) { items = next; render(); }
  // A countdown hitting zero needs the real server-checked state (clocks can drift a little,
  // and the owner may preview early) rather than trusting the browser's own tick.
  async function refresh() {
    const r = await api('/api/family/state'); if (r.ok && r.data.videos) setItems(r.data.videos);
  }
  function openModal() { openAddVideoModal({ onSaved: setItems }); }

  render();
}
