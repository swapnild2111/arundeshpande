(function () {
  var STORAGE_KEY = 'arundeshpande:ps-solved-v1';

  function safeRead() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return new Set();
      var arr = JSON.parse(raw);
      return new Set(Array.isArray(arr) ? arr.map(Number) : []);
    } catch (_) {
      return new Set();
    }
  }

  function safeWrite(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(set)));
      return true;
    } catch (_) {
      return false;
    }
  }

  function init() {
    var browser = document.querySelector('.ps-browser');
    var progressEl = document.querySelector('[data-ps-progress]');
    if (!browser || !progressEl) return;

    var textEl = progressEl.querySelector('[data-ps-progress-text]');
    var fillEl = progressEl.querySelector('[data-ps-progress-fill]');
    var resetBtn = progressEl.querySelector('[data-ps-progress-reset]');
    var template = progressEl.getAttribute('data-progress-template') || '{count} of {total}';
    var resetConfirm = progressEl.getAttribute('data-reset-confirm') || 'Clear progress?';

    // Read total from browser data attribute (Hugo renders data-group-size and data-group-count)
    // Fall back to counting DOM elements — all groups are in the DOM even when hidden
    var groupSize = parseInt(browser.getAttribute('data-group-size'), 10) || 10;
    var groupCount = parseInt(browser.getAttribute('data-group-count'), 10) || 1;
    var total = groupSize * groupCount;
    // Adjust for last group which may be smaller
    var domPairs = browser.querySelectorAll('.ps-pair[data-pair-num]');
    if (domPairs.length > 0) total = domPairs.length;

    if (total === 0) return;

    var storageOk = safeWrite(new Set()); // probe storage
    if (!storageOk) return;

    var solved = safeRead();
    applyState(solved);

    document.addEventListener('video-player:open', function (e) {
      var card = e.detail && e.detail.card;
      if (!card) return;
      if (!card.classList.contains('video-card--solution')) return;
      var pair = card.closest('.ps-pair[data-pair-num]');
      if (!pair) return;
      var num = parseInt(pair.getAttribute('data-pair-num'), 10);
      if (isNaN(num)) return;
      markSolved(num);
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        if (!confirm(resetConfirm)) return;
        solved = new Set();
        localStorage.removeItem(STORAGE_KEY);
        applyState(solved);
      });
    }

    function applyState(set) {
      // Re-query live so switching groups doesn't miss newly-visible pairs
      var allPairs = browser.querySelectorAll('.ps-pair[data-pair-num]');
      var count = 0;
      allPairs.forEach(function (pair) {
        var n = parseInt(pair.getAttribute('data-pair-num'), 10);
        if (!isNaN(n) && set.has(n)) {
          pair.classList.add('is-solved');
          count++;
        } else {
          pair.classList.remove('is-solved');
        }
      });

      var pct = total > 0 ? (count / total * 100) : 0;
      if (fillEl) fillEl.style.width = pct + '%';
      if (textEl) {
        textEl.textContent = template
          .replace('{count}', count)
          .replace('{total}', total);
      }
      progressEl.removeAttribute('hidden');
    }

    function markSolved(num) {
      if (solved.has(num)) return;
      solved.add(num);
      safeWrite(solved);
      applyState(solved);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
