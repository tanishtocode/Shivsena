// ═══════════════════════════════════════════════
// MANAGE SOCIAL WORK JS
// Clean + fixed version
// ═══════════════════════════════════════════════

// ── DROP ZONE ──────────────────────────────────
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewStrip = document.getElementById('previewStrip');

if (dropZone) {
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', function (e) {
        const files = e.dataTransfer.files;
        if (fileInput) {
            fileInput.files = files;
        }
        renderPreviews(files);
    });
}

if (fileInput) {
    fileInput.addEventListener('change', function () {
        renderPreviews(this.files);
    });
}

function renderPreviews(files) {
    if (!previewStrip) return;

    previewStrip.innerHTML = '';

    Array.from(files).forEach(file => {
        const wrap = document.createElement('div');
        wrap.className = 'sw-preview-thumb';

        const isVideo = file.type.startsWith('video/');
        const mediaEl = document.createElement(isVideo ? 'video' : 'img');

        mediaEl.src = URL.createObjectURL(file);

        if (isVideo) {
            mediaEl.muted = true;
            mediaEl.loop = true;
            mediaEl.autoplay = true;
            mediaEl.playsInline = true;
        }

        wrap.appendChild(mediaEl);
        previewStrip.appendChild(wrap);
    });
}

// ── EDIT MODAL ─────────────────────────────────
function openModalFromButton(button) {
    const id = button.dataset.id;
    const title = button.dataset.title || '';
    const description = button.dataset.description || '';
    const date = button.dataset.date || '';

    const editForm = document.getElementById('editForm');
    const editTitle = document.getElementById('editTitle');
    const editDesc = document.getElementById('editDesc');
    const editDate = document.getElementById('editDate');
    const editModal = document.getElementById('editModal');

    if (editForm) editForm.action = `/admin/social_work/edit/${id}`;
    if (editTitle) editTitle.value = title;
    if (editDesc) editDesc.value = description;
    if (editDate) editDate.value = date;
    if (editModal) editModal.classList.add('open');
}

function closeModal() {
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.classList.remove('open');
    }
}

const modalBackdrop = document.getElementById('editModal');
if (modalBackdrop) {
    modalBackdrop.addEventListener('click', function (e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

// Make functions globally accessible for inline onclick
window.openModalFromButton = openModalFromButton;
window.closeModal = closeModal;

// ── SEARCH FILTER ──────────────────────────────
const searchInput = document.getElementById('gallerySearch');
const noResults = document.getElementById('noResults');

if (searchInput) {
    searchInput.addEventListener('input', function () {
        const q = this.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.searchable-item');
        let visible = 0;

        cards.forEach(card => {
            const title = card.dataset.title || '';
            const desc = card.dataset.desc || '';
            const match = title.includes(q) || desc.includes(q);

            card.style.display = match ? '' : 'none';
            if (match) visible++;
        });

        if (noResults) {
            noResults.style.display = visible === 0 ? 'block' : 'none';
        }
    });
}

// ── VIDEO HOVER PLAY ───────────────────────────
document.querySelectorAll('.sw-card-media video').forEach(video => {
    const card = video.closest('.sw-card');

    if (card) {
        card.addEventListener('mouseenter', () => {
            video.play().catch(() => {});
        });

        card.addEventListener('mouseleave', () => {
            video.pause();
            video.currentTime = 0;
        });
    }
});