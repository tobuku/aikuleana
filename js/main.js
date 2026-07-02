/* ============================================
   AiKuleana.com - Main JavaScript
   ============================================ */

(function () {
  'use strict';

  /* ---------- Preloader ---------- */
  function killPreloader() {
    var el = document.getElementById('preloader');
    if (el) {
      el.classList.add('hidden');
      setTimeout(function () { el.remove(); }, 600);
    }
  }

  window.addEventListener('load', killPreloader);
  setTimeout(killPreloader, 3500); // safety net

  /* ---------- Navbar Scroll ---------- */
  var navbar = document.querySelector('.navbar');

  function handleNavScroll() {
    if (!navbar) return;
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll();

  /* ---------- Mobile Nav Toggle ---------- */
  var navToggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navToggle.classList.toggle('active');
      navLinks.classList.toggle('open');
      var expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
    });

    // Close mobile nav on link click
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navToggle.classList.remove('active');
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- Hero Image Rotation ---------- */
  var heroImages = document.querySelectorAll('.hero-bg img');
  var currentHeroIndex = 0;

  function rotateHeroImages() {
    if (heroImages.length === 0) return;
    heroImages[currentHeroIndex].classList.remove('active');
    currentHeroIndex = (currentHeroIndex + 1) % heroImages.length;
    heroImages[currentHeroIndex].classList.add('active');
  }

  if (heroImages.length > 0) {
    heroImages[0].classList.add('active');
    setInterval(rotateHeroImages, 5000);
  }

  /* ---------- Scroll Reveal ---------- */
  var revealElements = document.querySelectorAll('.reveal');

  function checkReveal() {
    var windowHeight = window.innerHeight;
    revealElements.forEach(function (el) {
      var top = el.getBoundingClientRect().top;
      if (top < windowHeight - 80) {
        el.classList.add('visible');
      }
    });
  }

  if (revealElements.length > 0) {
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

      revealElements.forEach(function (el) { observer.observe(el); });
    } else {
      window.addEventListener('scroll', checkReveal, { passive: true });
      checkReveal();
    }
  }

  /* ---------- Back to Top ---------- */
  var backToTop = document.querySelector('.back-to-top');

  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 600) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    }, { passive: true });

    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- Animated Counters ---------- */
  var counters = document.querySelectorAll('.stat-number[data-count]');

  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    var suffix = el.getAttribute('data-suffix') || '';
    var duration = 2000;
    var start = 0;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
      var current = Math.floor(eased * target);
      el.textContent = current.toLocaleString() + suffix;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target.toLocaleString() + suffix;
      }
    }

    requestAnimationFrame(step);
  }

  if (counters.length > 0 && 'IntersectionObserver' in window) {
    var counterObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(function (el) { counterObserver.observe(el); });
  }

  /* ---------- Newsletter Form ---------- */
  var newsletterForm = document.querySelector('.newsletter-form');

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = newsletterForm.querySelector('input[type="email"]');
      if (input && input.value) {
        var btn = newsletterForm.querySelector('button');
        btn.textContent = 'Mahalo!';
        btn.disabled = true;
        input.value = '';
        setTimeout(function () {
          btn.textContent = 'Subscribe';
          btn.disabled = false;
        }, 3000);
      }
    });
  }

})();
