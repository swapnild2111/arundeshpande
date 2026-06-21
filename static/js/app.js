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
      if (el.matches && el.matches('.video-grid, .book-grid, .gallery-grid, .chapter-grid')) {
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
})();
