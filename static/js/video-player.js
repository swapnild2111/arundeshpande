(function () {
  var modal;
  var iframe;
  var titleEl;
  var youtubeLink;
  var lastFocus;

  function embedUrl(id) {
    return 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id)
      + '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
  }

  function init() {
    modal = document.getElementById('video-player');
    if (!modal) return;

    iframe = document.getElementById('video-player-iframe');
    titleEl = document.getElementById('video-player-title');
    youtubeLink = document.getElementById('video-player-youtube');

    modal.querySelectorAll('[data-video-player-close]').forEach(function (node) {
      node.addEventListener('click', function (e) {
        e.preventDefault();
        close();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal && !modal.hidden) {
        e.preventDefault();
        close();
      }
    });

    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('.video-play-trigger');
      if (!trigger) return;
      var card = trigger.closest('.video-card[data-video-id]');
      if (!card) return;
      e.preventDefault();
      e.stopPropagation();
      openFromCard(card);
    });
  }

  function updateHash(slug) {
    if (!slug) return;
    var next = location.pathname + location.search + '#' + slug;
    if (location.pathname + location.search + location.hash === next) return;
    history.pushState(null, '', next);
  }

  function open(opts) {
    if (!modal || !iframe || !opts || !opts.id) return;

    lastFocus = document.activeElement;

    iframe.src = embedUrl(opts.id);
    titleEl.textContent = opts.title || '';
    youtubeLink.href = opts.youtube || ('https://www.youtube.com/watch?v=' + opts.id);

    modal.hidden = false;
    document.body.classList.add('video-player-open');

    if (opts.slug) updateHash(opts.slug);

    var closeBtn = modal.querySelector('.video-player-close');
    if (closeBtn) closeBtn.focus();
  }

  function close() {
    if (!modal || modal.hidden) return;

    iframe.src = '';
    modal.hidden = true;
    document.body.classList.remove('video-player-open');

    if (lastFocus && typeof lastFocus.focus === 'function') {
      lastFocus.focus();
    }
  }

  function openFromCard(card) {
    if (!card) return;
    open({
      id: card.getAttribute('data-video-id'),
      title: card.getAttribute('data-title') || '',
      youtube: card.getAttribute('data-youtube') || '',
      slug: card.getAttribute('data-anchor') || ''
    });
  }

  window.VideoPlayer = {
    open: open,
    close: close,
    openFromCard: openFromCard
  };

  document.addEventListener('DOMContentLoaded', init);
})();
