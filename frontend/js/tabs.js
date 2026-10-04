// Accessible tabs (WAI-ARIA pattern: roving tabindex, arrow/Home/End keys).
import { h } from './util.js';
let uid = 0;
export function makeTabs(labels, { onChange } = {}) {
  const id = 'tb' + (uid++);
  const list = h('div', { class: 'tabs', role: 'tablist' });
  const panels = labels.map((_, i) => h('div', { class: 'tabpanel' + (i ? ' hide' : ''), role: 'tabpanel', id: `${id}-p${i}`, 'aria-labelledby': `${id}-t${i}`, tabindex: '0' }));
  const tabs = labels.map((l, i) => h('button', { class: 'tab', role: 'tab', type: 'button', id: `${id}-t${i}`, 'aria-controls': `${id}-p${i}`, 'aria-selected': String(i === 0), tabindex: i ? '-1' : '0', text: l }));
  const select = (i, focus) => {
    tabs.forEach((t, j) => { t.setAttribute('aria-selected', String(i === j)); t.tabIndex = i === j ? 0 : -1; panels[j].classList.toggle('hide', i !== j); });
    if (focus) tabs[i].focus(); onChange && onChange(i);
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => select(i));
    t.addEventListener('keydown', e => {
      const k = { ArrowRight: (i + 1) % tabs.length, ArrowLeft: (i - 1 + tabs.length) % tabs.length, Home: 0, End: tabs.length - 1 }[e.key];
      if (k != null) { e.preventDefault(); select(k, true); }
    });
    list.append(t);
  });
  return { list, panels, select };
}
