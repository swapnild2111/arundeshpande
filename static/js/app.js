(function () {
  // Mobile sidebar toggle
  var toggle = document.querySelector('.nav-toggle');
  var sidebar = document.querySelector('.sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      var open = sidebar.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        closeLangSwitchers();
      }
    });
    sidebar.querySelectorAll('.nav-link[href]').forEach(function (link) {
      link.addEventListener('click', function () {
        sidebar.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function decodeWaPayload(encoded) {
    if (!encoded) return '';
    try {
      var binary = atob(encoded);
      var bytes = Uint8Array.from(binary, function (c) { return c.charCodeAt(0); });
      return new TextDecoder().decode(bytes);
    } catch (err) {
      return '';
    }
  }

  document.querySelectorAll('.js-wa-contact').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!e.isTrusted) return;
      var phone = decodeWaPayload(btn.getAttribute('data-wa-phone'));
      if (!phone) return;
      var text = decodeWaPayload(btn.getAttribute('data-wa-text'));
      var url = 'https://wa.me/' + phone;
      if (text) url += '?text=' + encodeURIComponent(text);
      window.open(url, '_blank', 'noopener,noreferrer');
    });
  });

  function closeLangSwitchers(except) {
    document.querySelectorAll('.lang-switcher.is-open').forEach(function (root) {
      if (except && root === except) return;
      root.classList.remove('is-open');
      var toggle = root.querySelector('.lang-switcher-toggle');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  }

  document.querySelectorAll('.lang-switcher').forEach(function (root) {
    var toggle = root.querySelector('.lang-switcher-toggle');
    var menu = root.querySelector('.lang-switcher-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !root.classList.contains('is-open');
      closeLangSwitchers();
      if (open) {
        root.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
      } else {
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        // Remember the user's pick so the root-URL auto-detect respects it
        // on future visits. The hreflang attribute carries the locale code.
        try {
          var code = link.getAttribute('hreflang');
          if (code) localStorage.setItem('site-lang', code);
        } catch (err) {}
        closeLangSwitchers();
      });
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.lang-switcher')) closeLangSwitchers();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLangSwitchers();
  });

  // PDF download buttons (books index + book hero). The green "Download
  // PDF" button opens a language picker; user explicitly chooses which
  // PDF to download. No auto-download for the current locale.
  function closePdfDownloads(except) {
    document.querySelectorAll('.pdf-download.is-open').forEach(function (root) {
      if (except && root === except) return;
      root.classList.remove('is-open');
      var trigger = root.querySelector('.pdf-download-trigger');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    });
  }
  document.querySelectorAll('.pdf-download').forEach(function (root) {
    var trigger = root.querySelector('.pdf-download-trigger');
    if (!trigger) return;
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      e.preventDefault();
      var open = !root.classList.contains('is-open');
      closePdfDownloads();
      if (open) {
        root.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
      } else {
        trigger.setAttribute('aria-expanded', 'false');
      }
    });
    // Closing the menu when a language is picked — the browser then
    // proceeds with the download (the anchor's default action).
    root.querySelectorAll('.pdf-download-item').forEach(function (link) {
      link.addEventListener('click', function () { closePdfDownloads(); });
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.pdf-download')) closePdfDownloads();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePdfDownloads();
  });

  function psBasePath() {
    var el = document.querySelector('[data-ps-base]');
    return el ? el.getAttribute('data-ps-base') : null;
  }

  function categoryFromHash() {
    var hash = location.hash.slice(1);
    if (!hash || !window.SiteUrls) return null;
    var target = window.SiteUrls.parse(hash);
    if (!target) return null;
    if (target.type === 'video-category') return target.id;
    if (target.type === 'book-category') return target.id;
    if (target.type === 'ps-group' || target.type === 'ps-item' || target.type === 'ps-home') {
      return null;
    }
    if (document.querySelector('.chip[data-filter="' + hash + '"]')) return hash;
    return null;
  }

  function setCategoryHash(filter) {
    var base = location.pathname + location.search;
    if (filter === 'all') {
      if (location.hash) history.replaceState(null, '', base);
      return;
    }
    history.replaceState(null, '', base + '#' + filter);
  }

  document.querySelectorAll('.chips').forEach(function (chips) {
    // Link-only chip nav (videos/books categories) is server-filtered — skip client filter.
    if (!chips.querySelector('.chip[data-filter]')) return;

    var el = chips.nextElementSibling;
    var grids = [];
    while (el) {
      if (el.matches && el.matches('.video-grid, .gallery-grid, .chapter-grid')) {
        grids.push(el);
      }
      el = el.nextElementSibling;
    }
    if (!grids.length) return;

    function applyFilter(filter) {
      grids.forEach(function (grid) {
        var showForAttr = grid.getAttribute('data-show-for');
        var showGrid = showForAttr
          ? showForAttr.split(/\s+/).indexOf(filter) !== -1
          : true;
        grid.style.display = showGrid ? '' : 'none';
        grid.hidden = !showGrid;
        if (!showGrid) return;

        var items = Array.prototype.slice.call(grid.children);
        items.forEach(function (it) {
          var tags = (it.getAttribute('data-tags') || '').split(/\s+/).filter(Boolean);
          if (!tags.length) return;
          it.style.display = (filter === 'all' || tags.indexOf(filter) !== -1) ? '' : 'none';
        });
      });
    }

    function activateChip(filter, options) {
      options = options || {};
      var chip = chips.querySelector('.chip[data-filter="' + filter + '"]');
      if (!chip) return;
      chips.querySelectorAll('.chip').forEach(function (c) { c.classList.remove('is-active'); });
      chip.classList.add('is-active');
      applyFilter(filter);
      if (options.updateHash !== false) setCategoryHash(filter);
    }

    window.__applyVideoFilter = applyFilter;
    window.__activateVideoCategory = activateChip;

    chips.querySelectorAll('.chip[data-filter]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        activateChip(chip.getAttribute('data-filter'));
      });
    });

    var fromHash = categoryFromHash();
    if (fromHash) {
      activateChip(fromHash, { updateHash: false });
    } else {
      var active = chips.querySelector('.chip.is-active[data-filter]');
      applyFilter(active ? active.getAttribute('data-filter') : 'all');
    }
  });

  // (The previous tier-tab toggle for "Watch in action" cards was removed —
  //  cards now stack all videos at once, no JS needed.)
})();
