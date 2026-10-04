// Shared helpers. Everything user- or AI-supplied is rendered with textContent / DOM nodes, never innerHTML.
export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
export const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
export const sleep = ms => new Promise(r => setTimeout(r, reduced ? Math.min(ms, 120) : ms));

export async function api(path, { method = 'GET', body } = {}) {
  const opts = { method, credentials: 'same-origin', headers: {} };
  if (method !== 'GET') { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body || {}); }
  try {
    const r = await fetch(path, opts);
    let data = {};
    try { data = await r.json(); } catch { /* non-JSON */ }
    return { ok: r.ok, status: r.status, data };
  } catch {
    return { ok: false, status: 0, data: { error: 'Network error. Please try again.' } };
  }
}

export function errText(r) {
  if (r.status === 429) return 'Too many attempts. Give it a moment and try again.';
  if (r.status === 503 && r.data.error === 'maintenance') return r.data.reason || 'The site is under maintenance.';
  return (r.data && r.data.error) || 'Something went wrong. Please try again.';
}

export function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return el;
}

export function toast(msg) {
  const t = $('#toast'); if (!t) return;
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2400);
}

export function copyText(text) { return navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject(); }

export function downloadText(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = h('a', { href: url, download: name }); document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function readFile(file, asDataUrl) {
  return new Promise((res, rej) => {
    const fr = new FileReader(); fr.onload = () => res(fr.result); fr.onerror = rej;
    asDataUrl ? fr.readAsDataURL(file) : fr.readAsText(file);
  });
}

// Tiny safe markdown: headings, bullets (nested under numbered items), numbered lists, rules, **bold**, *italic*,
// `code` and [links](https://...). Builds DOM nodes only; links are limited to http(s) and mailto.
const STAR = '\uE000';   // stands in for the literal * in "A*" so it can't open or close emphasis
const INLINE = /(`[^`]+`|\*\*(?=\S)(?:[^*]|\*(?!\*))+?\*\*|\[[^\]\n]+\]\((?:https?:\/\/|mailto:)[^\s)]+\)|(?<![*\w])\*(?=\S)[^*\n]+?(?<=\S)\*(?![*\w]))/;
const unstar = s => s.split(STAR).join('*');
export function renderMd(el, text) {
  el.textContent = '';
  const inline = (parent, s) => {
    s.split(INLINE).forEach(part => {
      if (!part) return;
      let m;
      if (part.length > 2 && part.startsWith('`') && part.endsWith('`')) parent.append(h('code', { text: unstar(part.slice(1, -1)) }));
      else if (part.length > 4 && part.startsWith('**') && part.endsWith('**')) { const b = h('strong'); inline(b, part.slice(2, -2)); parent.append(b); }
      else if ((m = part.match(/^\[([^\]]+)\]\(((?:https?:\/\/|mailto:)[^\s)]+)\)$/))) parent.append(h('a', { href: unstar(m[2]), target: '_blank', rel: 'noopener noreferrer', text: unstar(m[1]) }));
      else if (part.length > 2 && part.startsWith('*') && part.endsWith('*')) { const i = h('em'); inline(i, part.slice(1, -1)); parent.append(i); }
      else parent.append(document.createTextNode(unstar(part)));
    });
  };
  let list = null, para = [];
  const flushPara = () => { if (para.length) { const p = h('p'); para.forEach((line, i) => { if (i) p.append(h('br')); inline(p, line); }); el.append(p); para = []; } };
  const src = String(text).replace(/\r/g, '').replace(/\bA\*(?=\*\*(?!\*)|[^*]|$)/gm, 'A' + STAR);
  for (const raw of src.split('\n')) {
    const line = raw.trimEnd();
    let m;
    if (!line.trim()) { flushPara(); if (list && list.tagName !== 'OL') list = null; continue; }   // numbered lists survive blank lines
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) { flushPara(); list = null; el.append(h('hr')); continue; }
    if ((m = line.match(/^#{1,4}\s+(.*)$/))) { flushPara(); list = null; const hd = h('h4'); inline(hd, m[1]); el.append(hd); continue; }
    if ((m = line.match(/^\s*[-*•]\s+(.*)$/))) {
      flushPara();
      const li = h('li'); inline(li, m[1]);
      if (list && list.tagName === 'OL' && list.lastElementChild) {           // bullets under a numbered item
        const host = list.lastElementChild; let sub = host.lastElementChild;
        if (!sub || sub.tagName !== 'UL') { sub = h('ul'); host.append(sub); }
        sub.append(li); continue;
      }
      if (!list || list.tagName !== 'UL') { list = h('ul'); el.append(list); }
      list.append(li); continue;
    }
    if ((m = line.match(/^\s*(\d+)[.)]\s+(.*)$/))) {
      flushPara();
      if (!list || list.tagName !== 'OL') { list = h('ol'); if (+m[1] > 1) list.setAttribute('start', m[1]); el.append(list); }
      const li = h('li'); inline(li, m[2]); list.append(li); continue;
    }
    list = null; para.push(line);
  }
  flushPara();
}

// Reveal text progressively, re-rendering markdown as it grows.
export async function stream(el, text, onTick) {
  if (reduced || text.length > 2500) { renderMd(el, text); onTick && onTick(); return; }
  const words = text.split(/(\s+)/); let out = '';
  for (let i = 0; i < words.length; i++) {
    out += words[i];
    if (i % 4 === 0 || i === words.length - 1) { renderMd(el, out); onTick && onTick(); await new Promise(r => setTimeout(r, 16)); }
  }
}
