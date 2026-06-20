(function () {
  var browser = document.querySelector('.ps-browser');
  if (!browser) return;

  function U() {
    return window.SiteUrls;
  }
  var groupPanels = browser.querySelectorAll('[data-ps-group-panel]');
  var railItems = browser.querySelectorAll('[data-ps-rail]');
  var groupCount = parseInt(browser.getAttribute('data-group-count'), 10) || groupPanels.length;
  var pairTotal = browser.querySelectorAll('[data-ps-panel]').length;
  var stage = browser.querySelector('.ps-stage');

  function clampGroup(g) {
    return Math.max(1, Math.min(groupCount, parseInt(g, 10) || 1));
  }

  function groupMeta(g) {
    var panel = browser.querySelector('[data-ps-group-panel="' + g + '"]');
    if (!panel) return { start: 1, end: 10, group: 1 };
    return {
      start: parseInt(panel.getAttribute('data-ps-start'), 10),
      end: parseInt(panel.getAttribute('data-ps-end'), 10),
      group: g
    };
  }

  function groupFromRange(start, end) {
    var panel = browser.querySelector(
      '[data-ps-group-panel][data-ps-start="' + start + '"][data-ps-end="' + end + '"]'
    );
    if (panel) return parseInt(panel.getAttribute('data-ps-group-panel'), 10);
    var rail = browser.querySelector(
      '[data-ps-rail][data-ps-start="' + start + '"][data-ps-end="' + end + '"]'
    );
    if (rail) return parseInt(rail.getAttribute('data-ps-rail'), 10);
    return null;
  }

  function groupForProblem(num) {
    num = parseInt(num, 10) || 1;
    return clampGroup(Math.ceil(num / 10));
  }

  function updateHash(group, options) {
    if (options && options.updateHash === false) return;
    var urls = U();
    if (!urls) return;
    var meta = groupMeta(group);
    var base = location.pathname + location.search;
    history.replaceState(null, '', base + urls.hashPsGroup(meta.start, meta.end));
  }

  function updateProblemHash(num, options) {
    if (options && options.updateHash === false) return;
    var urls = U();
    if (!urls) return;
    var base = location.pathname + location.search;
    history.replaceState(null, '', base + urls.hashPsItem(num));
  }

  function showGroup(g, options) {
    options = options || {};
    g = clampGroup(g);

    groupPanels.forEach(function (panel) {
      var active = parseInt(panel.getAttribute('data-ps-group-panel'), 10) === g;
      panel.classList.toggle('is-active', active);
      if (active) panel.removeAttribute('hidden');
      else panel.setAttribute('hidden', '');
    });

    railItems.forEach(function (item) {
      var active = parseInt(item.getAttribute('data-ps-rail'), 10) === g;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-selected', active ? 'true' : 'false');
      if (active) {
        item.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
      }
    });

    if (stage) stage.scrollTop = 0;
    updateHash(g, options);
  }

  function showProblem(num, options) {
    options = options || {};
    num = Math.max(1, Math.min(pairTotal, parseInt(num, 10) || 1));
    var g = groupForProblem(num);
    showGroup(g, { updateHash: false });

    if (options.updateHash !== false) {
      updateProblemHash(num, options);
    }

    window.requestAnimationFrame(function () {
      var el = document.getElementById('ps-' + num) || browser.querySelector('[data-ps-panel="' + num + '"]');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  document.addEventListener('ps:show', function (e) {
    if (!e.detail || e.detail.num == null) return;
    showProblem(e.detail.num, { updateHash: e.detail.updateHash !== false });
  });

  document.addEventListener('ps:show-group', function (e) {
    if (!e.detail) return;
    var g = e.detail.group;
    if (g == null && e.detail.start != null && e.detail.end != null) {
      g = groupFromRange(e.detail.start, e.detail.end);
    }
    if (g != null) showGroup(g, { updateHash: e.detail.updateHash !== false });
  });

  railItems.forEach(function (item) {
    item.addEventListener('click', function () {
      showGroup(item.getAttribute('data-ps-rail'));
    });
  });

  document.addEventListener('keydown', function (e) {
    if (!browser.classList.contains('is-visible') && browser.getAttribute('data-standalone') !== 'true') return;
    if (browser.hidden) return;
    if (e.target.closest('input, textarea, select')) return;
    var current = browser.querySelector('[data-ps-group-panel].is-active');
    var g = current ? parseInt(current.getAttribute('data-ps-group-panel'), 10) : 1;
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      showGroup(g - 1);
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      showGroup(g + 1);
    }
  });

  function initFromHash() {
    var urls = U();
    if (!urls) return;
    var raw = location.hash.slice(1);
    var target = urls.parse(raw);
    if (!target) {
      showGroup(1);
      return;
    }

    if (target.type === 'ps-item') {
      showProblem(target.num, { updateHash: false });
      return;
    }

    if (target.type === 'ps-group') {
      var g = target.group;
      if (g == null && target.start != null && target.end != null) {
        g = groupFromRange(target.start, target.end);
      }
      if (g) {
        showGroup(g, { updateHash: !!target.legacy });
        return;
      }
    }

    if (target.type === 'anchor') {
      var psMatch = target.slug.match(/^(?:problem|solution)-(\d+)$/);
      if (psMatch) {
        showProblem(parseInt(psMatch[1], 10), { updateHash: false });
        return;
      }
    }

    showGroup(1);
  }

  if (browser.getAttribute('data-standalone') === 'true') {
    initFromHash();
  }
})();
