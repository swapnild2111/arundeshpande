(function () {
  var grid = document.querySelector('[data-gallery]');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.gallery-card'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.gallery-chip'));
  var lightbox = document.querySelector('[data-lightbox]');
  var lbImg = lightbox && lightbox.querySelector('[data-lb-img]');
  var lbCap = lightbox && lightbox.querySelector('[data-lb-caption]');
  var lbClose = lightbox && lightbox.querySelector('[data-lb-close]');
  var lbPrev = lightbox && lightbox.querySelector('[data-lb-prev]');
  var lbNext = lightbox && lightbox.querySelector('[data-lb-next]');
  var lbCopy = lightbox && lightbox.querySelector('[data-lb-copy]');
  var lbCopyToast = lightbox && lightbox.querySelector('[data-lb-copy-toast]');

  var HASH_PREFIX = '#photo=';

  // ---- Filters ------------------------------------------------------------
  function applyFilter(slug) {
    cards.forEach(function (card) {
      var tags = (card.getAttribute('data-tags') || '').split(/\s+/).filter(Boolean);
      var show = slug === 'all' || tags.indexOf(slug) !== -1;
      card.classList.toggle('is-hidden', !show);
    });
  }

  function activateChip(chip) {
    chips.forEach(function (c) {
      c.classList.remove('is-active');
      c.setAttribute('aria-pressed', 'false');
    });
    chip.classList.add('is-active');
    chip.setAttribute('aria-pressed', 'true');
    applyFilter(chip.getAttribute('data-filter'));
  }

  function resetToAllFilter() {
    var allChip = chips.filter(function (c) { return c.getAttribute('data-filter') === 'all'; })[0];
    if (allChip) activateChip(allChip);
    else applyFilter('all');
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () { activateChip(chip); });
  });

  // ---- Lightbox -----------------------------------------------------------
  if (!lightbox) return;

  // We manipulate the hash on open/step/close but should ignore the
  // resulting `hashchange` events (they're self-emitted). Only apply the
  // hash when it changed externally (back button, direct paste).
  var suppressHashHandler = false;
  var currentCard = null;

  function cardBySlug(slug) {
    if (!slug) return null;
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].getAttribute('data-slug') === slug) return cards[i];
    }
    return null;
  }

  function visibleCards() {
    return cards.filter(function (c) { return !c.classList.contains('is-hidden'); });
  }

  function setHash(slug) {
    suppressHashHandler = true;
    var next = slug ? (HASH_PREFIX + slug) : '';
    if (next) {
      history.replaceState(null, '', next);
    } else if (location.hash) {
      history.replaceState(null, '', location.pathname + location.search);
    }
    // Release the suppressor on the next tick (hashchange is async).
    setTimeout(function () { suppressHashHandler = false; }, 0);
  }

  function open(card, opts) {
    if (!card) return;
    opts = opts || {};
    // If the requested card is filtered out, drop the filter so we can show it.
    if (card.classList.contains('is-hidden')) resetToAllFilter();
    currentCard = card;
    render(card);
    if (!lightbox.hasAttribute('open')) {
      if (typeof lightbox.showModal === 'function') lightbox.showModal();
      else lightbox.setAttribute('open', '');
    }
    document.body.classList.add('gallery-lightbox-open');
    if (lbClose) lbClose.focus();
    if (!opts.skipHash) setHash(card.getAttribute('data-slug'));
  }

  function close(opts) {
    opts = opts || {};
    if (typeof lightbox.close === 'function') lightbox.close();
    else lightbox.removeAttribute('open');
    document.body.classList.remove('gallery-lightbox-open');
    lbImg.src = '';
    currentCard = null;
    if (!opts.skipHash) setHash(null);
  }

  function step(delta) {
    var visible = visibleCards();
    if (!visible.length) return;
    var idx = currentCard ? visible.indexOf(currentCard) : -1;
    if (idx === -1) idx = 0;
    idx = (idx + delta + visible.length) % visible.length;
    currentCard = visible[idx];
    render(currentCard);
    setHash(currentCard.getAttribute('data-slug'));
  }

  function render(card) {
    var btn = card.querySelector('.gallery-card-btn');
    if (!btn) return;
    lbImg.src = btn.getAttribute('data-src') || '';
    lbImg.alt = btn.getAttribute('data-caption') || '';
    lbCap.textContent = btn.getAttribute('data-caption') || '';
  }

  cards.forEach(function (card) {
    var btn = card.querySelector('.gallery-card-btn');
    if (!btn) return;
    btn.addEventListener('click', function () { open(card); });
  });

  lbClose && lbClose.addEventListener('click', function () { close(); });
  lbPrev && lbPrev.addEventListener('click', function () { step(-1); });
  lbNext && lbNext.addEventListener('click', function () { step(1); });

  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) close();
  });

  document.addEventListener('keydown', function (e) {
    if (!lightbox.hasAttribute('open')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
  });

  // <dialog> emits its own `close` when ESC is pressed — sync our state.
  lightbox.addEventListener('close', function () {
    document.body.classList.remove('gallery-lightbox-open');
    lbImg.src = '';
    currentCard = null;
    setHash(null);
  });

  // ---- Copy link ----------------------------------------------------------
  function showCopyToast() {
    if (!lbCopyToast) return;
    lbCopyToast.classList.add('is-visible');
    setTimeout(function () { lbCopyToast.classList.remove('is-visible'); }, 1600);
  }

  function copyCurrentLink() {
    if (!currentCard) return;
    var slug = currentCard.getAttribute('data-slug');
    var url = location.origin + location.pathname + location.search + HASH_PREFIX + slug;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(showCopyToast, function () {
        legacyCopy(url);
      });
    } else {
      legacyCopy(url);
    }
  }

  function legacyCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); showCopyToast(); } catch (e) { /* no-op */ }
    document.body.removeChild(ta);
  }

  lbCopy && lbCopy.addEventListener('click', copyCurrentLink);

  // ---- Deep link on load + hashchange -------------------------------------
  function openFromHash() {
    if (suppressHashHandler) return;
    var hash = location.hash || '';
    if (hash.indexOf(HASH_PREFIX) === 0) {
      var slug = hash.slice(HASH_PREFIX.length);
      var card = cardBySlug(slug);
      if (card) open(card, { skipHash: true });
      else close({ skipHash: true }); // unknown slug — leave lightbox shut
    } else {
      // Hash cleared (e.g. browser back button) — close if open.
      if (lightbox.hasAttribute('open')) close({ skipHash: true });
    }
  }

  window.addEventListener('hashchange', openFromHash);
  openFromHash(); // initial load
})();
