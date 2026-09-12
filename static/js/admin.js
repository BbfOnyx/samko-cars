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
    const renderPreviews = () => {
      previewGrid.replaceChildren();
      Array.from(imageInput.files).forEach((file, idx) => {
        if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) return;
        const reader = new FileReader();
        reader.onload = function (e) {
          const item = document.createElement('div');
          item.className = `image-preview-item${idx === 0 ? ' cover' : ''}`;
          const image = document.createElement('img');
          image.src = e.target.result;
          image.alt = 'Preview';
          const actions = document.createElement('div');
          actions.className = 'image-preview-actions';
          const removeButton = document.createElement('button');
          removeButton.type = 'button';
          removeButton.className = 'img-action-btn';
          removeButton.title = 'Remove';
          removeButton.textContent = '✕';
          removeButton.addEventListener('click', () => {
            const transfer = new DataTransfer();
            Array.from(imageInput.files).forEach((selectedFile, fileIndex) => {
              if (fileIndex !== idx) transfer.items.add(selectedFile);
            });
            imageInput.files = transfer.files;
            renderPreviews();
          });
          actions.appendChild(removeButton);
          item.append(image, actions);
          previewGrid.appendChild(item);
        };
        reader.readAsDataURL(file);
      });
    };

    imageInput.addEventListener('change', renderPreviews);
    imageInput.renderPreviews = renderPreviews;
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
        const transferred = new DataTransfer();
        Array.from(imageInput.files).forEach(f => transferred.items.add(f));
        Array.from(dt.files).forEach(f => transferred.items.add(f));
        imageInput.files = transferred.files;
        imageInput.dispatchEvent(new Event('change', { bubbles: true }));
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
