// Runs synchronously, before first paint, so a returning visitor to a private area never sees
// a flash of the default colour before shell.js confirms their role. Classic script (not a
// module) so it blocks parsing and executes immediately; shell.js removes this guess at boot
// and re-adds the confirmed theme, so a wrong guess self-corrects with no lasting effect.
(function () {
  try {
    var t = localStorage.getItem('kitsuneTheme');
    if (t === 'a' || t === 'b') document.documentElement.classList.add('theme-' + t);
  } catch (e) {}
})();
