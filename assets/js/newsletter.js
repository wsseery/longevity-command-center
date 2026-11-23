/* Longevity Command Center newsletter sign-up (site-wide, shared by /finance and blog posts).
   Posts the .lcc-newsletter-form to Agile CRM in the background with the single tag
   lcc-newsletter, then confirms on the page. The LCC list is separate and is never
   cross-mailed with any other venture (GLOBAL §6a #8). Without fetch, the plain GET
   submit still reaches Agile. */
(function () {
  var forms = document.querySelectorAll('form.lcc-newsletter-form');
  Array.prototype.forEach.call(forms, function (f) {
    f.addEventListener('submit', function (ev) {
      if (window.gtag) window.gtag('event', 'sign_up', { method: 'lcc_newsletter' });
      if (!window.fetch || !window.URLSearchParams || !window.FormData) return;
      ev.preventDefault();
      var btn = f.querySelector('[type=submit]');
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var url = f.action + '?' + new URLSearchParams(new FormData(f)).toString();
      var shown = false;
      function done() {
        if (shown) return; shown = true;
        var ok = f.querySelector('.lcc-newsletter-sent');
        Array.prototype.forEach.call(f.children, function (c) { if (c !== ok && c.type !== 'hidden') c.hidden = true; });
        if (ok) { ok.hidden = false; ok.setAttribute('tabindex', '-1'); ok.focus(); }
      }
      // Agile can take 10+ seconds to answer; keepalive lets the request finish if the
      // visitor leaves, so confirm after 2.5 s or on the response, whichever is first.
      var timer = setTimeout(done, 2500);
      fetch(url, { method: 'GET', mode: 'no-cors', credentials: 'omit', keepalive: true })
        .then(done)
        .catch(function () { clearTimeout(timer); if (!shown) f.submit(); });
    });
  });
})();
