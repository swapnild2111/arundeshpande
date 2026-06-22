(function () {
  function U() {
    return window.SiteUrls;
  }

  function requireU() {
    var urls = U();
    if (!urls) console.warn('SiteUrls not loaded');
    return urls;
  }

  function psBasePath() {
    var el = document.querySelector('[data-ps-base]');
    if (el) return el.getAttribute('data-ps-base');
    var browser = document.querySelector('.ps-browser[data-ps-base]');
    return browser ? browser.getAttribute('data-ps-base') : null;
  }

  function videosRoot() {
    var el = document.querySelector('[data-videos-root]');
    return el ? el.getAttribute('data-videos-root') : '/videos/';
  }

  function booksRoot() {
    var el = document.querySelector('[data-books-root]');
    return el ? el.getAttribute('data-books-root') : '/books/';
  }

  function isBooksSection() {
    return /\/books(\/|$)/.test(location.pathname);
  }

  function categoryUrl(cat) {
    var root = videosRoot();
    if (root.charAt(root.length - 1) !== '/') root += '/';
    if (cat === 'all') return root;
    if (cat === 'problems-solutions') {
      var ps = psBasePath();
      return ps || root + 'problems-solutions/';
    }
    return root + cat + '/';
  }

  function bookCategoryUrl(cat) {
    var root = booksRoot();
    if (root.charAt(root.length - 1) !== '/') root += '/';
    if (cat === 'all') return root;
    return root + cat + '/';
  }

  function onPsPage() {
    return /\/problems-solutions\/?$/.test(location.pathname);
  }

  function onCategoryPage(cat) {
    if (cat === 'problems-solutions') return onPsPage();
    if (cat === 'all') return /\/videos\/?$/.test(location.pathname);
    return new RegExp('/videos/' + cat + '/?$').test(location.pathname);
  }

  function onBookCategoryPage(cat) {
    if (cat === 'all') return /\/books\/?$/.test(location.pathname);
    return new RegExp('/books/' + cat + '/?$').test(location.pathname);
  }

  function redirectTo(url) {
    if (location.pathname + location.search + location.hash === url) return false;
    location.replace(url);
    return true;
  }

  function redirectToPsPage(hash) {
    var base = psBasePath();
    if (!base || onPsPage()) return false;
    return redirectTo(base + (hash || ''));
  }

  function redirectToCategory(cat, hash) {
    if (onCategoryPage(cat)) return false;
    return redirectTo(categoryUrl(cat) + (hash || ''));
  }

  function redirectToBookCategory(cat, hash) {
    if (onBookCategoryPage(cat)) return false;
    return redirectTo(bookCategoryUrl(cat) + (hash || ''));
  }

  function psGroupRange(g) {
    var panel = document.querySelector('[data-ps-group-panel="' + g + '"]');
    if (panel) {
      return {
        start: parseInt(panel.getAttribute('data-ps-start'), 10),
        end: parseInt(panel.getAttribute('data-ps-end'), 10)
      };
    }
    var browser = document.querySelector('.ps-browser');
    var size = browser ? parseInt(browser.getAttribute('data-group-size'), 10) || 10 : 10;
    return { start: (g - 1) * size + 1, end: g * size };
  }

  function psGroupHashFromTarget(target) {
    var urls = U();
    if (!urls) return '';
    if (target.start != null && target.end != null) {
      return urls.hashPsGroup(target.start, target.end);
    }
    if (target.group != null) {
      var range = psGroupRange(target.group);
      return urls.hashPsGroup(range.start, range.end);
    }
    return '';
  }

  function maybeNormalizeLegacyHash() {
    var urls = U();
    if (!urls) return false;
    var raw = location.hash.slice(1);
    if (!raw) return false;
    var norm = urls.normalizeHash(raw);
    if (!norm || !norm.changed || !norm.hash) return false;
    var base = location.pathname + location.search;
    if (location.hash === norm.hash) return false;
    history.replaceState(null, '', base + norm.hash);
    return true;
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
    var urls = requireU();
    if (!urls) return false;

    maybeNormalizeLegacyHash();

    var raw = location.hash.slice(1);
    var hash = location.hash;
    var target = urls.parse(raw);

    if (target && (target.type === 'ps-group' || target.type === 'ps-item' || target.type === 'ps-home')) {
      if (!onPsPage() && redirectToPsPage(hash)) return true;
    }

    if (target && target.type === 'anchor') {
      var earlyEl = urls.findAnchor(target.slug);
      if (!earlyEl) {
        var cat = urls.videoCategoryFromSlug(target.slug);
        if (cat && redirectToCategory(cat, urls.hashAnchor(target.slug))) return true;
      }
    }

    if (target && target.type === 'video-category') {
      if (redirectToCategory(target.id, '')) return true;
    }

    if (target && target.type === 'book-category' && isBooksSection()) {
      if (redirectToBookCategory(target.id, '')) return true;
    }

    if (!target) return false;

    if (target.type === 'ps-home') {
      if (!onPsPage()) {
        redirectToPsPage(urls.hashPsGroup(1, 10));
      } else {
        document.dispatchEvent(new CustomEvent('ps:show-group', {
          detail: { start: 1, end: 10, updateHash: true }
        }));
      }
      return true;
    }

    if (target.type === 'book-category') {
      if (target.id === 'all') {
        if (!onBookCategoryPage('all')) location.replace(bookCategoryUrl('all'));
        return true;
      }
      redirectToBookCategory(target.id, '');
      return true;
    }

    if (target.type === 'video-category') {
      if (target.id === 'problems-solutions') {
        redirectToPsPage(urls.hashPsGroup(1, 10));
        return true;
      }
      if (target.id === 'all') {
        if (!onCategoryPage('all')) location.replace(categoryUrl('all'));
        return true;
      }
      redirectToCategory(target.id, '');
      return true;
    }

    if (target.type === 'ps-group') {
      var groupHash = psGroupHashFromTarget(target);
      if (!onPsPage()) {
        if (groupHash) redirectToPsPage(groupHash);
        return true;
      }
      document.dispatchEvent(new CustomEvent('ps:show-group', {
        detail: {
          group: target.group,
          start: target.start,
          end: target.end,
          updateHash: false
        }
      }));
      if (target.legacy && groupHash) {
        history.replaceState(null, '', location.pathname + location.search + groupHash);
      }
      return true;
    }

    if (target.type === 'ps-item') {
      if (!onPsPage()) {
        redirectToPsPage(urls.hashPsItem(target.num));
        return true;
      }
      document.dispatchEvent(new CustomEvent('ps:show', {
        detail: { num: target.num, updateHash: false }
      }));
      return true;
    }

    if (target.type === 'anchor') {
      var el = urls.findAnchor(target.slug);
      if (!el) {
        var inferred = urls.videoCategoryFromSlug(target.slug);
        if (inferred && redirectToCategory(inferred, urls.hashAnchor(target.slug))) return true;
        return false;
      }

      var psCtx = urls.psContextFromAnchor(el, target.slug);
      if (!isNaN(psCtx.num)) {
        if (!onPsPage()) {
          redirectToPsPage(urls.hashPsItem(psCtx.num));
          return true;
        }
        document.dispatchEvent(new CustomEvent('ps:show', {
          detail: { num: psCtx.num, updateHash: false }
        }));
        window.setTimeout(function () { highlightAndScroll(el); }, 120);
        if (el.getAttribute('data-video-id') && window.VideoPlayer) {
          window.setTimeout(function () {
            window.VideoPlayer.openFromCard(el);
          }, 320);
        }
        return true;
      }

      if (el.id && el.id.indexOf('book-') === 0) {
        var bookCat = el.getAttribute('data-category') || el.getAttribute('data-tags') || 'other';
        var bookSlug = target.slug;
        if (isBooksSection() && !onBookCategoryPage(bookCat)) {
          redirectToBookCategory(bookCat, urls.hashAnchor(bookSlug));
          return true;
        }
        highlightAndScroll(el);
        return true;
      }

      var videoCat = el.getAttribute('data-category') || urls.videoCategoryFromSlug(target.slug) || 'misc';
      if (!onCategoryPage(videoCat)) {
        redirectToCategory(videoCat, urls.hashAnchor(target.slug));
        return true;
      }
      highlightAndScroll(el);
      if (el.getAttribute('data-video-id') && window.VideoPlayer) {
        window.setTimeout(function () {
          window.VideoPlayer.openFromCard(el);
        }, 200);
      }
      return true;
    }

    return false;
  }

  window.addEventListener('hashchange', applyDeepLink);
  document.addEventListener('DOMContentLoaded', applyDeepLink);
})();
