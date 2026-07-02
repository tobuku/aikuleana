/* ============================================
   AiKuleana.com - Bake Stands Page JS
   ============================================ */

(function () {
  'use strict';

  /* ---------- Filter Tags Toggle ---------- */
  var filterTags = document.querySelectorAll('.filter-tag');
  var bakeCards = document.querySelectorAll('.bake-card');
  var resultsCount = document.getElementById('results-count');

  function getActiveFilters() {
    var active = [];
    filterTags.forEach(function (tag) {
      if (tag.classList.contains('active')) {
        active.push(tag.getAttribute('data-filter'));
      }
    });
    return active;
  }

  function filterCards() {
    var active = getActiveFilters();
    var searchTerm = '';
    var searchInput = document.getElementById('bake-search');
    if (searchInput) {
      searchTerm = searchInput.value.toLowerCase().trim();
    }

    var neighborhoodSelect = document.getElementById('filter-neighborhood');
    var selectedNeighborhood = neighborhoodSelect ? neighborhoodSelect.value : '';

    var priceSelect = document.getElementById('filter-price');
    var selectedPrice = priceSelect ? priceSelect.value : '';

    var visibleCount = 0;

    bakeCards.forEach(function (card) {
      var cardTags = (card.getAttribute('data-tags') || '').split(',');
      var cardName = (card.getAttribute('data-name') || '').toLowerCase();
      var cardNeighborhood = card.getAttribute('data-neighborhood') || '';
      var cardPrice = card.getAttribute('data-price') || '';

      var matchesFilters = active.length === 0 || active.some(function (f) {
        return cardTags.indexOf(f) !== -1;
      });

      var matchesSearch = !searchTerm || cardName.indexOf(searchTerm) !== -1;
      var matchesNeighborhood = !selectedNeighborhood || cardNeighborhood === selectedNeighborhood;
      var matchesPrice = !selectedPrice || cardPrice === selectedPrice;

      if (matchesFilters && matchesSearch && matchesNeighborhood && matchesPrice) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (resultsCount) {
      resultsCount.textContent = visibleCount + ' bake stand' + (visibleCount !== 1 ? 's' : '');
    }
  }

  filterTags.forEach(function (tag) {
    tag.addEventListener('click', function () {
      tag.classList.toggle('active');
      filterCards();
    });
  });

  // Search input
  var searchInput = document.getElementById('bake-search');
  if (searchInput) {
    var debounceTimer;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(filterCards, 200);
    });
  }

  // Dropdown filters
  var neighborhoodSelect = document.getElementById('filter-neighborhood');
  var priceSelect = document.getElementById('filter-price');

  if (neighborhoodSelect) {
    neighborhoodSelect.addEventListener('change', filterCards);
  }
  if (priceSelect) {
    priceSelect.addEventListener('change', filterCards);
  }

  // Clear all filters
  var clearBtn = document.querySelector('.filter-clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      filterTags.forEach(function (tag) { tag.classList.remove('active'); });
      if (searchInput) searchInput.value = '';
      if (neighborhoodSelect) neighborhoodSelect.value = '';
      if (priceSelect) priceSelect.value = '';
      filterCards();
    });
  }

  /* ---------- Section Tabs ---------- */
  var sectionTabs = document.querySelectorAll('.section-tab');
  var tabSections = document.querySelectorAll('[data-tab-content]');

  sectionTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = tab.getAttribute('data-tab');

      sectionTabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');

      if (target === 'all') {
        tabSections.forEach(function (s) { s.style.display = ''; });
      } else {
        tabSections.forEach(function (s) {
          s.style.display = s.getAttribute('data-tab-content') === target ? '' : 'none';
        });
      }
    });
  });

  /* ---------- Favorite Toggle ---------- */
  document.querySelectorAll('.card-favorite').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      btn.classList.toggle('liked');
      var label = btn.classList.contains('liked') ? 'Remove from favorites' : 'Add to favorites';
      btn.setAttribute('aria-label', label);
    });
  });

  /* ---------- Sticky Filter Shadow ---------- */
  var filterSection = document.querySelector('.filter-section');
  if (filterSection) {
    var navHeight = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-height')) || 72;

    window.addEventListener('scroll', function () {
      if (filterSection.getBoundingClientRect().top <= navHeight + 1) {
        filterSection.classList.add('has-shadow');
      } else {
        filterSection.classList.remove('has-shadow');
      }
    }, { passive: true });
  }

})();
