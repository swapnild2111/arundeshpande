(function () {
  function parseHash() {
    var raw = location.hash.slice(1);
    if (!raw) return null;
    if (raw.indexOf('v-') === 0) return { type: 'video', slug: raw.slice(2) };
    if (raw.indexOf('ps-') === 0) return { type: 'ps', num: parseInt(raw.slice(3), 10) };
    if (raw.indexOf('book-') === 0) return { type: 'book', slug: raw.slice(5) };
    return null;
  }

  function activateFilter(filterId) {
    var chip = document.querySelector('.chip[data-filter="' + filterId + '"]');
    if (chip) chip.click();
  }

  function highlightAndScroll(el) {
    if (!el) return;
    document.querySelectorAll('.is-deep-linked').forEach(function (node) {
      node.classList.remove('is-deep-linked');
    });
    el.classList.add('is-deep-linked');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    window.setTimeout(function () {
      el.classList.remove('is-deep-linked');
    }, 2400);
  }

  function applyDeepLink() {
    var target = parseHash();
    if (!target) return false;

    if (target.type === 'ps' && !isNaN(target.num)) {
      activateFilter('problems-solutions');
      document.dispatchEvent(new CustomEvent('ps:show', {
        detail: { num: target.num, updateHash: false }
      }));
      return true;
    }

    if (target.type === 'video' && target.slug) {
      var el = document.getElementById('v-' + target.slug);
      if (!el) {
        el = document.querySelector('.video-card[data-video-id="' + target.slug + '"]');
      }
      if (!el) return false;

      var pair = el.closest('[data-ps-panel]');
      if (pair) {
        activateFilter('problems-solutions');
        document.dispatchEvent(new CustomEvent('ps:show', {
          detail: {
            num: parseInt(pair.getAttribute('data-ps-panel'), 10),
            updateHash: false
          }
        }));
        window.setTimeout(function () { highlightAndScroll(el); }, 80);
      } else {
        var card = el.closest('.video-card');
        var tags = (card && card.getAttribute('data-tags') || '')
          .split(/\s+/).filter(Boolean);
        activateFilter(tags.length ? tags[0] : 'all');
        highlightAndScroll(el);
      }
      return true;
    }

    if (target.type === 'book' && target.slug) {
      var book = document.getElementById('book-' + target.slug);
      if (!book) return false;
      var tag = book.getAttribute('data-tags');
      if (tag) activateFilter(tag);
      highlightAndScroll(book);
      return true;
    }

    return false;
  }

  document.addEventListener('click', function (e) {
    var play = e.target.closest('.play-btn');
    var card = e.target.closest('.video-card[data-youtube]');
    if (play && card) {
      e.preventDefault();
      e.stopPropagation();
      window.open(card.getAttribute('data-youtube'), '_blank', 'noopener');
    }
  });

  window.addEventListener('hashchange', applyDeepLink);
  document.addEventListener('DOMContentLoaded', applyDeepLink);
})();
