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
  }

  // Filter chips: toggle grids and filter items by data-tags
  document.querySelectorAll('.chips').forEach(function (chips) {
    var el = chips.nextElementSibling;
    var grids = [];
    while (el) {
      if (el.matches && el.matches('.video-grid, .book-grid, .gallery-grid, .chapter-grid, .pair-grid, .ps-browser')) {
        grids.push(el);
      }
      el = el.nextElementSibling;
    }
    if (!grids.length) return;

    function applyFilter(filter) {
      grids.forEach(function (grid) {
        var showForAttr = grid.getAttribute('data-show-for');
        var isPairBrowser = grid.classList.contains('pair-grid') || grid.classList.contains('ps-browser');
        var showGrid;
        if (isPairBrowser) {
          showGrid = showForAttr && showForAttr.split(/\s+/).indexOf(filter) !== -1;
        } else if (showForAttr) {
          showGrid = showForAttr.split(/\s+/).indexOf(filter) !== -1;
        } else {
          showGrid = true;
        }
        if (isPairBrowser) {
          grid.classList.toggle('is-visible', showGrid);
          grid.hidden = !showGrid;
        } else {
          grid.style.display = showGrid ? '' : 'none';
          grid.hidden = !showGrid;
        }
        if (!showGrid || isPairBrowser) return;

        var items = Array.prototype.slice.call(grid.children);
        items.forEach(function (it) {
          var tags = (it.getAttribute('data-tags') || '').split(/\s+/).filter(Boolean);
          if (!tags.length) return;
          it.style.display = (filter === 'all' || tags.indexOf(filter) !== -1) ? '' : 'none';
        });
      });
    }

    chips.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.querySelectorAll('.chip').forEach(function (c) { c.classList.remove('is-active'); });
        chip.classList.add('is-active');
        applyFilter(chip.getAttribute('data-filter'));
      });
    });

    var active = chips.querySelector('.chip.is-active');
    applyFilter(active ? active.getAttribute('data-filter') : 'all');
  });
})();
