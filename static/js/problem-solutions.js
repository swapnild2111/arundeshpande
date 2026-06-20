(function () {
  var browser = document.querySelector('.ps-browser');
  if (!browser) return;

  var panels = browser.querySelectorAll('[data-ps-panel]');
  var items = browser.querySelectorAll('[data-ps-num]');
  var jump = browser.querySelector('[data-ps-jump]');
  var counter = browser.querySelector('[data-ps-counter]');
  var total = panels.length;

  function show(num, options) {
    options = options || {};
    num = Math.max(1, Math.min(total, parseInt(num, 10) || 1));
    panels.forEach(function (panel) {
      var active = parseInt(panel.getAttribute('data-ps-panel'), 10) === num;
      panel.hidden = !active;
      panel.classList.toggle('is-active', active);
    });
    items.forEach(function (item) {
      var active = parseInt(item.getAttribute('data-ps-num'), 10) === num;
      item.classList.toggle('is-active', active);
      if (active) item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
    if (jump) jump.value = num;
    if (counter) counter.textContent = num + ' / ' + total;
    if (options.updateHash !== false) {
      history.replaceState(null, '', '#ps-' + num);
    }
  }

  document.addEventListener('ps:show', function (e) {
    if (!e.detail || e.detail.num == null) return;
    show(e.detail.num, { updateHash: e.detail.updateHash !== false });
  });

  items.forEach(function (item) {
    item.addEventListener('click', function () {
      show(item.getAttribute('data-ps-num'));
    });
  });

  if (jump) {
    jump.addEventListener('blur', function () { show(jump.value); });
    jump.addEventListener('wheel', function (e) { e.preventDefault(); }, { passive: false });
    jump.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        show(jump.value);
        jump.blur();
      }
    });
  }

  browser.querySelectorAll('[data-ps-prev]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var current = parseInt(jump && jump.value ? jump.value : '1', 10) || 1;
      show(current - 1);
    });
  });

  browser.querySelectorAll('[data-ps-next]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var current = parseInt(jump && jump.value ? jump.value : '1', 10) || 1;
      show(current + 1);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (!browser.classList.contains('is-visible') || browser.hidden) return;
    if (e.target.closest('input, textarea, select')) return;
    var current = parseInt(jump && jump.value ? jump.value : '1', 10) || 1;
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      show(current - 1);
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      show(current + 1);
    }
  });

  if (!/^#(ps-|v-)/.test(location.hash)) {
    show(1, { updateHash: false });
  }
})();
