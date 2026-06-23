document.addEventListener('DOMContentLoaded', function () {
    // 🔧 Слайдер карточек
    function initDealSlider() {
        const container = document.querySelector('.deal-slider__container');
        const prevBtn = document.querySelector('.deal-slider__prev-btn');
        const nextBtn = document.querySelector('.deal-slider__next-btn');
        const dotsContainer = document.querySelector('.deal-slider__dots');

        if (!container) return;

        const cards = container.querySelectorAll('.deal-card');
        let currentIndex = 0;
        const total = cards.length;

        // Создаём точки
        dotsContainer.innerHTML = '';
        for (let i = 0; i < total; i++) {
            const dot = document.createElement('div');
            dot.className = 'deal-slider__dot' + (i === 0 ? ' active' : '');
            dot.dataset.index = i;
            dot.addEventListener('click', () => slideTo(i));
            dotsContainer.appendChild(dot);
        }

        function slideTo(index) {
            currentIndex = Math.max(0, Math.min(index, total - 1));
            container.style.transform = `translateX(-${currentIndex * 100}%)`;

            // Обновляем точки
            dotsContainer.querySelectorAll('.deal-slider__dot').forEach((dot, i) => {
                dot.classList.toggle('active', i === currentIndex);
            });
        }

        if (prevBtn) prevBtn.addEventListener('click', () => slideTo(currentIndex - 1));
        if (nextBtn) nextBtn.addEventListener('click', () => slideTo(currentIndex + 1));

        // Тач-свайп для мобильных
        let startX = 0;
        let isTouching = false;

        container.addEventListener('touchstart', e => {
            startX = e.touches[0].clientX;
            isTouching = true;
        });

        container.addEventListener('touchend', e => {
            if (!isTouching) return;
            const endX = e.changedTouches[0].clientX;
            const diff = endX - startX;

            if (Math.abs(diff) > 50) { // порог свайпа
                if (diff > 0) slideTo(currentIndex - 1);
                else slideTo(currentIndex + 1);
            }
            isTouching = false;
        });
    }

    // Запуск после загрузки
    document.addEventListener('DOMContentLoaded', () => {
        // ... ваш код таймера ...
        initDealSlider();
    });

    function updateCountdown() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(now.getDate() + 1);
        tomorrow.setHours(36, 0, 0, 0);

        const diff = tomorrow - now;

        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        const hoursEl = document.getElementById('hours');
        const minutesEl = document.getElementById('minutes');
        const secondsEl = document.getElementById('seconds');

        if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, '0');
        if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, '0');
        if (secondsEl) secondsEl.textContent = seconds.toString().padStart(2, '0');
    }

    setInterval(updateCountdown, 1000);
    updateCountdown();
});
