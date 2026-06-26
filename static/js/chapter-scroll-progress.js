/*
 * Drives the .chapter-progress-bar width based on how far the visitor
 * has scrolled through the chapter's <article class="book-prose">.
 *
 * - 0%   when the top of the article is still below the rail
 * - 100% when the bottom of the article has scrolled past the rail
 *
 * We measure progress against the article (not the whole page) so the
 * bar doesn't keep filling while the visitor scrolls through the
 * unrelated footer.
 *
 * Updates throttled via requestAnimationFrame, plus a fresh measure
 * on resize/orientationchange because the sticky rail's height (and
 * therefore the "is fully visible" baseline) can shift.
 */
(function () {
  var bar = document.querySelector('.chapter-progress-bar');
  var rail = document.querySelector('.chapter-rail');
  var article = document.querySelector('.chapter .book-prose');
  if (!bar || !article) return;

  function progress() {
    var rect = article.getBoundingClientRect();
    // viewport area below the rail's actual painted bottom edge —
    // accounts for mobile-header offset when the rail is sitting
    // below it, and uses the rail's real height (not assumed).
    var viewportTop = rail ? rail.getBoundingClientRect().bottom : 0;
    var viewportBottom = window.innerHeight || document.documentElement.clientHeight;
    var visibleHeight = viewportBottom - viewportTop;
    if (visibleHeight <= 0) return 0;

    // distance scrolled past the top of the article, in pixels.
    // 0 when article top is still below viewportTop, grows as we scroll past.
    var scrolledPast = viewportTop - rect.top;
    if (scrolledPast <= 0) return 0;

    // How much article content lives below the rail, plus the part we've
    // already passed. We want the bar full when the article bottom hits
    // the rail — i.e. when scrolledPast === article.height - visibleHeight.
    var denom = rect.height - visibleHeight;
    if (denom <= 0) {
      // Article fits entirely in the visible viewport — call it "done"
      // as soon as the user starts scrolling at all.
      return scrolledPast > 0 ? 100 : 0;
    }
    var ratio = scrolledPast / denom;
    if (ratio < 0) return 0;
    if (ratio > 1) return 100;
    return ratio * 100;
  }

  var pending = false;
  function update() {
    pending = false;
    var p = progress();
    bar.style.width = p + '%';
    bar.parentElement.setAttribute('aria-valuenow', Math.round(p));
  }
  function schedule() {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(update);
  }

  // Initial paint after layout settles.
  update();
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  window.addEventListener('orientationchange', schedule);
})();
