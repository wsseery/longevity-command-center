/* Longevity Command Center newsletter sign-up (site-wide, shared by /finance and blog posts).
   Sends the .lcc-newsletter-form email to Agile CRM in the background with the single tag
   lcc-newsletter (the form's hidden "tags" field), then confirms on the page. The LCC list is
   separate and is never cross-mailed with any other venture (GLOBAL §6a #8).

   AGILE holds the only Agile web-form path on file: the shared Agile account and its
   "Website Listings Inquiry" form. The key is Agile's web-form tracking key, public by
   design (Agile embeds it in every website form). Change only these values if Bill sets
   up a dedicated "LCC Newsletter" form. The box stays hidden without JavaScript. */
(function () {
  var AGILE = {
    url: 'https://savingsre.agilecrm.com/formsubmit',
    fields: {
      _agile_form_name: 'Website Listings Inquiry',
      _agile_domain: 'savingsre',
      _agile_api: 'o8d0am3m1ras18l8f0r0qai4hq',
      _agile_form_id: '6520129726382080',
      _agile_redirect_url: 'https://longevitycommandcenter.com/?newsletter=sent',
      _agile_confirmation_msg: "Thanks. You're on the list."
    }
  };
  var forms = document.querySelectorAll('form.lcc-newsletter-form');
  Array.prototype.forEach.call(forms, function (f) {
    f.action = AGILE.url;
    Object.keys(AGILE.fields).forEach(function (k) {
      var i = document.createElement('input');
      i.type = 'hidden'; i.name = k; i.value = AGILE.fields[k];
      f.insertBefore(i, f.firstChild);
    });
    var box = f.closest('.lcc-newsletter');
    if (box) box.hidden = false;
    f.addEventListener('submit', function (ev) {
      if (window.gtag) window.gtag('event', 'sign_up', { method: 'lcc_newsletter' });
      if (!window.fetch || !window.URLSearchParams || !window.FormData) return;
      ev.preventDefault();
      var btn = f.querySelector('[type=submit]');
      if (btn) { btn.disabled = true; btn.value = 'Sending…'; }
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
