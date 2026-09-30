/* ================================================================
   ShopEasy — Main JavaScript
================================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Navbar scroll shadow ── */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 10);
    });
  }

  /* ── Mobile hamburger menu ── */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
      // Animate bars
      const bars = hamburger.querySelectorAll('span');
      if (open) {
        bars[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        bars[1].style.opacity = '0';
        bars[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
      }
    });
  }

  /* ── Auto-dismiss toasts ── */
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity .4s, transform .4s';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  });

  /* ── Product detail: qty +/- buttons ── */
  const qtyMinus = document.getElementById('qty-minus');
  const qtyPlus  = document.getElementById('qty-plus');
  const qtyInput = document.getElementById('qty-input');
  if (qtyMinus && qtyPlus && qtyInput) {
    qtyMinus.addEventListener('click', () => {
      const v = parseInt(qtyInput.value) || 1;
      if (v > 1) qtyInput.value = v - 1;
    });
    qtyPlus.addEventListener('click', () => {
      const v = parseInt(qtyInput.value) || 1;
      const max = parseInt(qtyInput.max) || 999;
      if (v < max) qtyInput.value = v + 1;
    });
  }

  /* ── Cart inline qty +/- ── */
  document.querySelectorAll('.qty-form').forEach(form => {
    const minus = form.querySelector('[data-delta="-1"]');
    const plus  = form.querySelector('[data-delta="1"]');
    const input = form.querySelector('.qty-input-inline');
    if (minus && plus && input) {
      minus.addEventListener('click', () => {
        const v = parseInt(input.value) || 1;
        if (v > 1) input.value = v - 1;
      });
      plus.addEventListener('click', () => {
        input.value = (parseInt(input.value) || 1) + 1;
      });
    }
  });

  /* ── Payment option toggle ── */
  document.querySelectorAll('.payment-opt').forEach(opt => {
    opt.addEventListener('click', () => {
      document.querySelectorAll('.payment-opt').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
    });
  });

  /* ── Password show/hide toggle ── */
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      const isPass = input.type === 'password';
      input.type = isPass ? 'text' : 'password';
      const icon = btn.querySelector('i');
      icon.className = isPass ? 'fas fa-eye-slash' : 'fas fa-eye';
    });
  });

  /* ── Password strength meter ── */
  const pwd1 = document.getElementById('id_password1');
  const strengthWrap = document.getElementById('pwd-strength');
  const strengthFill = document.getElementById('strength-fill');
  const strengthLabel = document.getElementById('strength-label');
  if (pwd1 && strengthWrap && strengthFill && strengthLabel) {
    pwd1.addEventListener('input', () => {
      const val = pwd1.value;
      strengthWrap.style.display = val.length ? 'block' : 'none';
      let score = 0;
      if (val.length >= 8)  score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      const levels = [
        { pct: '25%', color: '#ef4444', label: 'Weak' },
        { pct: '50%', color: '#f59e0b', label: 'Fair' },
        { pct: '75%', color: '#3b82f6', label: 'Good' },
        { pct: '100%', color: '#10b981', label: 'Strong' },
      ];
      const lvl = levels[Math.max(0, score - 1)];
      strengthFill.style.width = lvl.pct;
      strengthFill.style.background = lvl.color;
      strengthLabel.textContent = lvl.label;
      strengthLabel.style.color = lvl.color;
    });
  }

  /* ── Smooth scroll for anchor links ── */
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Cart badge live update after add-to-cart ── */
  const addForms = document.querySelectorAll('form[action*="cart/add"]');
  addForms.forEach(form => {
    form.addEventListener('submit', () => {
      const badge = document.getElementById('cart-badge');
      if (badge) {
        const current = parseInt(badge.textContent) || 0;
        badge.textContent = current + 1;
        badge.classList.remove('hidden');
        // Bounce animation
        badge.style.transform = 'scale(1.5)';
        setTimeout(() => { badge.style.transform = ''; }, 300);
      }
    });
  });

  /* ── Add-to-cart button feedback ── */
  document.querySelectorAll('.add-cart-btn:not(.disabled)').forEach(btn => {
    btn.addEventListener('click', function() {
      const icon = this.querySelector('i');
      if (!icon) return;
      icon.className = 'fas fa-check';
      this.style.background = '#10b981';
      setTimeout(() => {
        icon.className = 'fas fa-shopping-cart';
        this.style.background = '';
      }, 1200);
    });
  });

  /* ── Input number clamp ── */
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('change', () => {
      const min = parseInt(input.min) || 1;
      const max = parseInt(input.max) || 9999;
      if (parseInt(input.value) < min) input.value = min;
      if (parseInt(input.value) > max) input.value = max;
    });
  });

  /* ── Simple fade-in animation on scroll ── */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('[data-aos]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity .6s ease, transform .6s ease';
    observer.observe(el);
  });

});
