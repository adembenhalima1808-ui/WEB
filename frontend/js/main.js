import { $, api } from './util.js';
import { createGate } from './gate.js';
import { buildApp } from './shell.js';

async function enter() {
  const [me, cfgRes] = await Promise.all([api('/api/auth/me'), api('/api/config')]);
  const cfg = cfgRes.ok ? cfgRes.data : {};
  const role = me.ok ? me.data.role : null;
  $('#gate').classList.add('hide');
  await buildApp({ role, cfg, me: me.ok ? me.data : {} });
  $('#main').focus({ preventScroll: true });
}

(async function boot() {
  const gate = createGate({ onEnter: enter });
  const me = await api('/api/auth/me');
  if (me.ok && me.data.maintenance && me.data.role !== 'admin') return gate.showOffline(me.data.maintenance_reason);
  if (me.ok && me.data.init) return enter();
  gate.showStart();
})();
