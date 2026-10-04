// Radar chart as inline SVG (no library). Colours come from CSS variables so every theme just works.
const NS = 'http://www.w3.org/2000/svg';
// Break a label into at most two lines of about `max` characters, so long names never run off a phone screen.
function wrap(label, max) {
  if (label.length <= max) return [label];
  const words = label.split(/\s+/); let a = '';
  while (words.length && (a + ' ' + words[0]).trim().length <= max) a = (a + ' ' + words.shift()).trim();
  if (!a) a = words.shift();
  let b = words.join(' ');
  if (b.length > max + 2) b = b.slice(0, max).trimEnd() + '\u2026';
  return b ? [a, b] : [a];
}

export function drawRadar(container, cats, scores) {
  container.textContent = '';
  const n = cats.length; if (!n) return;
  const C = 0, R = 130;
  const pt = (i, v) => { const a = -Math.PI / 2 + (2 * Math.PI * i) / n; return [C + Math.cos(a) * R * v, C + Math.sin(a) * R * v]; };
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '-250 -185 500 370'); svg.setAttribute('class', 'radar');
  svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'Radar chart: ' + cats.map((c, i) => `${c} ${scores[i]}`).join(', '));
  const mk = (tag, attrs, cls, text) => { const el = document.createElementNS(NS, tag); for (const k in attrs) el.setAttribute(k, attrs[k]); if (cls) el.setAttribute('class', cls); if (text != null) el.textContent = text; svg.append(el); return el; };
  [0.25, 0.5, 0.75, 1].forEach(v => mk('polygon', { points: cats.map((_, i) => pt(i, v).join(',')).join(' ') }, 'grid'));
  cats.forEach((c, i) => {
    const [x, y] = pt(i, 1); mk('line', { x1: 0, y1: 0, x2: x, y2: y }, 'spoke');
    const [lx, ly] = pt(i, 1.14);
    const lines = wrap(String(c), 18), top = ly < -R * 0.9, bottom = ly > R * 0.9;
    const t = mk('text', { x: lx, y: ly, 'text-anchor': lx < -8 ? 'end' : lx > 8 ? 'start' : 'middle' });
    const first = top ? -(lines.length - 1) * 1.15 + 'em' : bottom ? '0.8em' : (0.35 - (lines.length - 1) * 0.575) + 'em';
    lines.forEach((ln, j) => { const ts = document.createElementNS(NS, 'tspan'); ts.setAttribute('x', lx); ts.setAttribute('dy', j ? '1.15em' : first); ts.textContent = ln; t.append(ts); });
  });
  mk('polygon', { points: scores.map((s, i) => pt(i, Math.max(0, Math.min(100, s)) / 100).join(',')).join(' ') }, 'shape');
  scores.forEach((s, i) => { const [x, y] = pt(i, Math.max(0, Math.min(100, s)) / 100); mk('circle', { cx: x, cy: y, r: 3 }, 'dot'); });
  container.append(svg);
}
