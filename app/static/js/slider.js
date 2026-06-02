document.addEventListener("DOMContentLoaded", function () {

    // ─────────────────────────────────────────────
    // HERO SLIDER
    // ─────────────────────────────────────────────

    const slides = document.querySelectorAll(".hero-slide");
    const prevBtn = document.getElementById("prevSlide");
    const nextBtn = document.getElementById("nextSlide");

    let current = 0;
    let autoTimer = null;

    function showSlide(index) {
        slides.forEach(slide => {
            slide.classList.remove("active");
        });

        if (slides[index]) {
            slides[index].classList.add("active");
        }
    }

    function nextSlide() {
        current = (current + 1) % slides.length;
        showSlide(current);
    }

    function prevSlide() {
        current = (current - 1 + slides.length) % slides.length;
        showSlide(current);
    }

    function startAuto() {
        autoTimer = setInterval(nextSlide, 3500);
    }

    function resetAuto() {
        clearInterval(autoTimer);
        startAuto();
    }

    if (slides.length > 0) {

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                nextSlide();
                resetAuto();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                prevSlide();
                resetAuto();
            });
        }

        let touchStartX = 0;

        const slider = document.getElementById("heroSlider");

        if (slider) {

            slider.addEventListener("touchstart", (e) => {
                touchStartX = e.touches[0].clientX;
            });

            slider.addEventListener("touchend", (e) => {

                const diff =
                    touchStartX - e.changedTouches[0].clientX;

                if (diff > 50) {
                    nextSlide();
                    resetAuto();
                }

                else if (diff < -50) {
                    prevSlide();
                    resetAuto();
                }
            });
        }

        showSlide(current);
        startAuto();
    }

    // ─────────────────────────────────────────────
    // GALLERY SCROLL
    // ─────────────────────────────────────────────

    const strip = document.getElementById("galleryStrip");
    const btnLeft = document.getElementById("galleryLeft");
    const btnRight = document.getElementById("galleryRight");

    const SCROLL_BY = 520;

    if (strip && btnLeft && btnRight) {

        btnLeft.addEventListener("click", () => {
            strip.scrollBy({
                left: -SCROLL_BY,
                behavior: "smooth"
            });
        });

        btnRight.addEventListener("click", () => {
            strip.scrollBy({
                left: SCROLL_BY,
                behavior: "smooth"
            });
        });

        function updateArrows() {

            btnLeft.style.opacity =
                strip.scrollLeft > 10 ? "1" : "0.3";

            btnRight.style.opacity =
                strip.scrollLeft <
                strip.scrollWidth - strip.clientWidth - 10
                    ? "1"
                    : "0.3";
        }

        strip.addEventListener("scroll", updateArrows);

        updateArrows();
    }

    // ─────────────────────────────────────────────
    // LIGHTBOX
    // ─────────────────────────────────────────────

    const items = window.galleryItems || [];

    let lbIndex = 0;

    window.openLightbox = function (index) {

        if (!items.length) return;

        lbIndex = index;

        renderLightbox();

        document
            .getElementById("galleryLightbox")
            .classList.add("open");

        document.body.style.overflow = "hidden";
    };

    window.closeLightbox = function () {

        document
            .getElementById("galleryLightbox")
            .classList.remove("open");

        document.body.style.overflow = "";

        const vid =
            document.querySelector("#lightboxMedia video");

        if (vid) {
            vid.pause();
        }
    };

    window.shiftLightbox = function (dir) {

        lbIndex =
            (lbIndex + dir + items.length) % items.length;

        renderLightbox();
    };

    function renderLightbox() {

        const item = items[lbIndex];

        if (!item) return;

        const media =
            document.getElementById("lightboxMedia");

        const info =
            document.getElementById("lightboxInfo");

        if (item.type === "video") {

            media.innerHTML = `
                <video
                    src="${item.src}"
                    controls
                    autoplay
                    muted
                    playsinline
                    style="width:100%;max-height:80vh;"
                ></video>
            `;
        }

        else {

            media.innerHTML = `
                <img
                    src="${item.src}"
                    alt="${item.title}"
                    style="width:100%;max-height:80vh;object-fit:contain;"
                >
            `;
        }

        info.innerHTML = `
            <h3>${item.title}</h3>
            ${item.date ? `<p>📅 ${item.date}</p>` : ""}
        `;

        const showNav = items.length > 1;

        document.getElementById("lbPrev").style.display =
            showNav ? "flex" : "none";

        document.getElementById("lbNext").style.display =
            showNav ? "flex" : "none";
    }

    const lightbox =
        document.getElementById("galleryLightbox");

    if (lightbox) {

        lightbox.addEventListener("click", function (e) {

            if (e.target === this) {
                closeLightbox();
            }
        });
    }

    document.addEventListener("keydown", function (e) {

        const lb =
            document.getElementById("galleryLightbox");

        if (!lb || !lb.classList.contains("open")) {
            return;
        }

        if (e.key === "Escape") {
            closeLightbox();
        }

        if (e.key === "ArrowRight") {
            shiftLightbox(1);
        }

        if (e.key === "ArrowLeft") {
            shiftLightbox(-1);
        }
    });

});