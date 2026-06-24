/* ══════════════════════════════════════════════
   MAISON ROUGE — Main JS
   ══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Navbar scroll effect ── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Mobile hamburger ── */
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => navLinks.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!hamburger.contains(e.target) && !navLinks.contains(e.target))
        navLinks.classList.remove('open');
    });
  }

  /* ── Food particle spawner (hero) ── */
  const particleHost = document.getElementById('heroParticles');
  if (particleHost) {
    const foods = ['🍷','🥂','🍾','🫕','🍋','🌿','🧄','🍅','🫐','🌶','🫚','🍃','✦'];
    let particleId = 0;
    function spawnParticle() {
      const el = document.createElement('span');
      el.classList.add('food-particle');
      el.textContent = foods[Math.floor(Math.random() * foods.length)];
      el.style.left   = Math.random() * 100 + '%';
      el.style.bottom = '-40px';
      const dur   = 5 + Math.random() * 6;
      const delay = Math.random() * 2;
      el.style.setProperty('--dur',   dur + 's');
      el.style.setProperty('--delay', delay + 's');
      el.style.fontSize = (1 + Math.random() * 1.4) + 'rem';
      particleHost.appendChild(el);
      setTimeout(() => el.remove(), (dur + delay) * 1000 + 500);
    }
    setInterval(spawnParticle, 900);
    // Kick off a few immediately
    for (let i = 0; i < 5; i++) setTimeout(spawnParticle, i * 300);
  }

  /* ── Auth page particles ── */
  const authParticles = document.getElementById('authParticles');
  if (authParticles) {
    const symbols = ['✦','·','◦','✧','⟡','◈'];
    for (let i = 0; i < 18; i++) {
      const el = document.createElement('span');
      el.style.cssText = `
        position:absolute;
        left:${Math.random()*100}%;
        top:${Math.random()*100}%;
        font-size:${0.6+Math.random()*1.2}rem;
        color:rgba(201,149,66,${0.05+Math.random()*0.12});
        animation:bob ${3+Math.random()*4}s ease-in-out ${Math.random()*3}s infinite;
        pointer-events:none;
      `;
      el.textContent = symbols[Math.floor(Math.random()*symbols.length)];
      authParticles.appendChild(el);
    }
  }

  /* ── Scroll reveal ── */
  const revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          setTimeout(() => e.target.classList.add('visible'), i * 60);
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    revealEls.forEach(el => io.observe(el));
  }

  /* ── Animated counter ── */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const countIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el     = entry.target;
          const target = parseInt(el.getAttribute('data-count'), 10);
          const suffix = el.getAttribute('data-suffix') || '';
          const dur    = 1800;
          const start  = performance.now();
          function tick(now) {
            const pct = Math.min((now - start) / dur, 1);
            // ease-out cubic
            const ease = 1 - Math.pow(1 - pct, 3);
            el.textContent = Math.round(target * ease) + suffix;
            if (pct < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          countIo.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => countIo.observe(el));
  }

  /* ── Toast auto-dismiss ── */
  document.querySelectorAll('.toast').forEach(toast => {
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismissToast(toast));
    setTimeout(() => dismissToast(toast), 5000);
  });

  function dismissToast(el) {
    el.style.transition = 'all .35s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateX(24px)';
    setTimeout(() => el.remove(), 380);
  }

  /* ── Menu category filter ── */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const menuCards  = document.querySelectorAll('.menu-card[data-category]');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.getAttribute('data-filter');
      menuCards.forEach(card => {
        const show = cat === 'all' || card.getAttribute('data-category') === cat;
        card.style.display = show ? '' : 'none';
        if (show) {
          card.style.animation = 'none';
          card.offsetHeight; // reflow
          card.style.animation = 'fadeInUp .4s ease both';
        }
      });
    });
  });

  /* ── Reservation countdown ── */
  document.querySelectorAll('[data-res-date]').forEach(el => {
    const dateStr = el.getAttribute('data-res-date');
    const target  = new Date(dateStr);
    const now     = new Date();
    const diff    = Math.ceil((target - now) / 86400000);
    if (diff > 0 && diff <= 7) {
      const badge = el.querySelector('.countdown-badge');
      if (badge) badge.textContent = diff === 1 ? 'Tomorrow!' : `In ${diff} days`;
    }
  });

  /* ── Stagger reveal for cards on load ── */
  document.querySelectorAll('.menu-card, .res-card, .testimonial-card, .feature-item').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    const io2 = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            el.style.transition = 'opacity .5s ease, transform .5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
          }, (i % 6) * 80);
          io2.unobserve(el);
        }
      });
    }, { threshold: 0.1 });
    io2.observe(el);
  });

  /* ── Fork wiggle on hover (hero plate) ── */
  const plate = document.querySelector('.plate-center');
  if (plate) {
    plate.addEventListener('mouseenter', () => {
      plate.style.animation = 'wiggle .4s ease';
      setTimeout(() => plate.style.animation = '', 450);
    });
  }

});
