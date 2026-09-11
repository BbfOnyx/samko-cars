/* =====================================================
   SAMKO CARS — Admin Panel JavaScript
   ===================================================== */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (Mobile) ─────────────────────────
  const sidebarToggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('admin-sidebar');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', function (e) {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          !sidebarToggleBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Image Preview on File Input ─────────────────────
  const imageInput = document.getElementById('id_images');
  const previewGrid = document.getElementById('image-preview-grid');

  if (imageInput && previewGrid) {
    imageInput.addEventListener('change', function () {
      const files = Array.from(this.files);
      files.forEach((file, idx) => {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = function (e) {
          const item = document.createElement('div');
          item.className = `image-preview-item${idx === 0 ? ' cover' : ''}`;
          item.innerHTML = `
            <img src="${e.target.result}" alt="Preview">
            <div class="image-preview-actions">
              <button type="button" class="img-action-btn" onclick="this.closest('.image-preview-item').remove()" title="Remove">✕</button>
            </div>
            ${idx === 0 ? '<div style="position:absolute;bottom:4px;left:4px;background:var(--color-primary);color:#1a1a1a;font-size:0.6rem;font-weight:700;padding:1px 5px;border-radius:4px;">COVER</div>' : ''}
          `;
          previewGrid.appendChild(item);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // ── Drag & Drop Upload Area ─────────────────────────
  const uploadArea = document.getElementById('upload-area');
  if (uploadArea && imageInput) {
    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', function (e) {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function () {
      uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function (e) {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      const dt = e.dataTransfer;
      if (dt.files.length) {
        // Create a new DataTransfer to combine existing + dropped
        const transferred = new DataTransfer();
        Array.from(dt.files).forEach(f => transferred.items.add(f));
        imageInput.files = transferred.files;
        imageInput.dispatchEvent(new Event('change'));
      }
    });
  }

  // ── Delete Confirm Dialogs ──────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      const msg = this.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  // ── Flash alert auto-dismiss ────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // ── Auto-grow textarea ──────────────────────────────
  document.querySelectorAll('textarea.form-control').forEach(ta => {
    ta.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = this.scrollHeight + 'px';
    });
  });
});
