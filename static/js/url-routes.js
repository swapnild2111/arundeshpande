(function (global) {
  var VIDEO_CATS = ['beginner', 'intermediate', 'champion', 'misc'];
  var BOOK_CATS = ['students', 'coaches', 'rules', 'other'];

  var LOCALIZED_PREFIX = {
    'begynder-': 'beginner',
    'mellem-': 'intermediate',
    'mester-': 'champion',
    'anfanger-': 'beginner',
    'fortgeschritten-': 'intermediate',
    'misc-': 'misc'
  };

  function parse(raw) {
    if (!raw) return null;

    var m = raw.match(/^ps(\d+)-(\d+)$/);
    if (m) {
      return { type: 'ps-group', start: parseInt(m[1], 10), end: parseInt(m[2], 10) };
    }

    m = raw.match(/^ps-(\d+)$/);
    if (m) return { type: 'ps-item', num: parseInt(m[1], 10) };

    m = raw.match(/^ps-g(\d+)$/);
    if (m) return { type: 'ps-group', group: parseInt(m[1], 10), legacy: true };

    if (raw.indexOf('v-') === 0) {
      return { type: 'anchor', slug: raw.slice(2), legacy: true };
    }
    if (raw.indexOf('book-') === 0) {
      return { type: 'anchor', slug: raw.slice(5), legacy: true };
    }

    if (raw === 'problems-solutions') return { type: 'ps-home' };
    if (VIDEO_CATS.indexOf(raw) !== -1) return { type: 'video-category', id: raw, legacy: true };
    if (BOOK_CATS.indexOf(raw) !== -1) return { type: 'book-category', id: raw, legacy: true };

    if (/^(problem|solution)-\d+$/.test(raw) || raw.indexOf('-') !== -1) {
      return { type: 'anchor', slug: raw };
    }

    return null;
  }

  function hashPsGroup(start, end) {
    return '#ps' + start + '-' + end;
  }

  function hashPsItem(num) {
    return '#ps-' + num;
  }

  function hashAnchor(slug) {
    return '#' + slug;
  }

  function normalizeHash(raw) {
    var target = parse(raw);
    if (!target) return null;

    if (target.type === 'ps-group') {
      if (target.start != null && target.end != null) {
        return { target: target, hash: hashPsGroup(target.start, target.end), changed: !!target.legacy };
      }
      return { target: target, hash: null, changed: false };
    }

    if (target.type === 'ps-item') {
      return { target: target, hash: hashPsItem(target.num), changed: false };
    }

    if (target.type === 'anchor') {
      return { target: target, hash: hashAnchor(target.slug), changed: !!target.legacy };
    }

    return { target: target, hash: '#' + raw, changed: false };
  }

  function videoCategoryFromSlug(slug) {
    var i;
    for (i = 0; i < VIDEO_CATS.length; i++) {
      if (slug.indexOf(VIDEO_CATS[i] + '-') === 0) return VIDEO_CATS[i];
    }
    var prefix;
    for (prefix in LOCALIZED_PREFIX) {
      if (slug.indexOf(prefix) === 0) return LOCALIZED_PREFIX[prefix];
    }
    return null;
  }

  function findAnchor(slug) {
    if (!slug) return null;
    return document.getElementById('v-' + slug)
      || document.getElementById('book-' + slug)
      || document.querySelector('[data-anchor="' + slug + '"]');
  }

  function psContextFromAnchor(el, slug) {
    var panel = el ? el.closest('[data-ps-panel]') : null;
    var num = panel ? parseInt(panel.getAttribute('data-ps-panel'), 10) : NaN;
    if (isNaN(num) && slug) {
      var match = slug.match(/^(?:problem|solution)-(\d+)$/);
      if (match) num = parseInt(match[1], 10);
    }
    return { panel: panel, num: num };
  }

  global.SiteUrls = {
    VIDEO_CATS: VIDEO_CATS,
    BOOK_CATS: BOOK_CATS,
    parse: parse,
    normalizeHash: normalizeHash,
    hashPsGroup: hashPsGroup,
    hashPsItem: hashPsItem,
    hashAnchor: hashAnchor,
    videoCategoryFromSlug: videoCategoryFromSlug,
    findAnchor: findAnchor,
    psContextFromAnchor: psContextFromAnchor
  };
})(window);
