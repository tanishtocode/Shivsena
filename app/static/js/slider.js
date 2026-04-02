document.addEventListener("DOMContentLoaded", function () {

    // ── Hero Slider (index.html) ──────────────────────────
    const slides   = document.querySelectorAll(".hero-slide");
    const prevBtn  = document.getElementById("prevSlide");
    const nextBtn  = document.getElementById("nextSlide");

    if (slides.length === 0) return;

    let current   = 0;
    let autoTimer = null;

    function showSlide(index) {
        slides.forEach(s => s.classList.remove("active"));
        slides[index].classList.add("active");
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

    if (nextBtn) {
        nextBtn.addEventListener("click", () => { nextSlide(); resetAuto(); });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", () => { prevSlide(); resetAuto(); });
    }

    // Swipe support for mobile
    let touchStartX = 0;

    const slider = document.getElementById("heroSlider");

    if (slider) {
        slider.addEventListener("touchstart", (e) => {
            touchStartX = e.touches[0].clientX;
        });

        slider.addEventListener("touchend", (e) => {
            const diff = touchStartX - e.changedTouches[0].clientX;
            if (diff > 50)       { nextSlide(); resetAuto(); }
            else if (diff < -50) { prevSlide(); resetAuto(); }
        });
    }

    showSlide(current);
    startAuto();
});