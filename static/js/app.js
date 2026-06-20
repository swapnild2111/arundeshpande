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

  // Filter chips: filter sibling grid items by data-tags
  document.querySelectorAll('.chips').forEach(function (chips) {
    var grid = chips.nextElementSibling;
    while (grid && !grid.matches('.video-grid, .book-grid, .gallery-grid, .chapter-grid')) {
      grid = grid.nextElementSibling;
    }
    if (!grid) return;
    var items = Array.prototype.slice.call(grid.children);
    chips.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.querySelectorAll('.chip').forEach(function (c) { c.classList.remove('is-active'); });
        chip.classList.add('is-active');
        var f = chip.getAttribute('data-filter');
        items.forEach(function (it) {
          var tags = (it.getAttribute('data-tags') || '').split(/\s+/);
          it.style.display = (f === 'all' || tags.indexOf(f) !== -1) ? '' : 'none';
        });
      });
    });
  });
})();
