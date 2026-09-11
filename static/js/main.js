/* =====================================================
   SAMKO CARS — Main JavaScript
   Theme toggle, hamburger, modals, toasts, gallery
   ===================================================== */

// ── Theme Toggle ──────────────────────────────────────
(function () {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('samko-theme') || 'light';
  root.setAttribute('data-theme', savedTheme);

  function initThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    function updateIcon(theme) {
      btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }

    updateIcon(savedTheme);

    btn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('samko-theme', next);
      updateIcon(next);
    });
  }

  document.addEventListener('DOMContentLoaded', initThemeToggle);
})();

// ── Hamburger Menu ────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      const isOpen = mobileMenu.classList.contains('open');
      hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', !isOpen);
      document.body.style.overflow = isOpen ? '' : 'hidden';
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      }
    });

    // Keyboard (Escape)
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  }
});

// ── Toast Notifications ───────────────────────────────
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-size:1.2rem;flex-shrink:0">${icons[type] || icons.info}</span>
    <div style="flex:1;font-size:0.875rem;color:var(--text-primary)">${message}</div>
    <button onclick="this.closest('.toast').remove()" style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1rem;flex-shrink:0">✕</button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// ── Modals ────────────────────────────────────────────
function openModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (overlay) {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (overlay) {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  });

  // Close modal buttons
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modalId = this.getAttribute('data-close-modal');
      closeModal(modalId);
    });
  });

  // Open modal buttons
  document.querySelectorAll('[data-open-modal]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modalId = this.getAttribute('data-open-modal');
      openModal(modalId);
    });
  });
});

// ── AJAX Enquiry Form ─────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const enquiryForms = document.querySelectorAll('[data-enquiry-form]');
  enquiryForms.forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector('[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      const formData = new FormData(form);
      formData.append('is_ajax', '1');

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        if (data.success) {
          showToast(data.message, 'success');
          form.reset();
          // Close modal if inside one
          const modal = form.closest('.modal-overlay');
          if (modal) {
            setTimeout(() => {
              modal.classList.remove('open');
              document.body.style.overflow = '';
            }, 1500);
          }
        } else {
          showToast(data.message || 'Please check all fields and try again.', 'error');
        }
      } catch (err) {
        showToast('Network error. Please try again.', 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  });
});

// ── AJAX Purchase Form ────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const purchaseForms = document.querySelectorAll('[data-purchase-form]');
  purchaseForms.forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector('[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';

      const formData = new FormData(form);
      formData.append('is_ajax', '1');

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        if (data.success) {
          showToast(data.message, 'success');
          form.reset();
          const modal = form.closest('.modal-overlay');
          if (modal) {
            setTimeout(() => {
              modal.classList.remove('open');
              document.body.style.overflow = '';
            }, 2000);
          }
        } else {
          showToast(data.message || 'Please fill all required fields.', 'error');
        }
      } catch (err) {
        showToast('Network error. Please try again.', 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  });
});

// ── Image Gallery (Car Detail) ────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const mainImg = document.getElementById('gallery-main-img');
  const thumbs = document.querySelectorAll('.gallery-thumb');

  if (mainImg && thumbs.length) {
    thumbs.forEach(thumb => {
      thumb.addEventListener('click', function () {
        mainImg.src = this.getAttribute('data-src');
        mainImg.alt = this.getAttribute('data-alt') || '';
        thumbs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }
});

// ── Price Range Filter Sync ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const minPriceInput = document.getElementById('id_min_price');
  const maxPriceInput = document.getElementById('id_max_price');

  function formatNaira(val) {
    const num = parseInt(val.replace(/\D/g, ''));
    return isNaN(num) ? '' : num.toLocaleString('en-NG');
  }
});

// ── Auto-dismiss Django flash messages ────────────────
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
});

// ── Filter Sidebar Toggle (Mobile) ───────────────────
document.addEventListener('DOMContentLoaded', function () {
  const filterToggle = document.getElementById('filter-toggle');
  const filterSidebar = document.getElementById('filter-sidebar');

  if (filterToggle && filterSidebar) {
    filterToggle.addEventListener('click', function () {
      const isOpen = filterSidebar.style.display === 'block';
      filterSidebar.style.display = isOpen ? 'none' : 'block';
      filterToggle.textContent = isOpen ? '🔍 Show Filters' : '✕ Hide Filters';
    });
  }
});

// ── Navbar scroll effect ──────────────────────────────
(function () {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  window.addEventListener('scroll', function () {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 4px 24px rgba(0,0,0,0.15)';
    } else {
      navbar.style.boxShadow = '';
    }
  }, { passive: true });
})();
