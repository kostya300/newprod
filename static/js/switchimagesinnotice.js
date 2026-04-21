document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.thumb');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function () {
            // Убираем активный класс со всех
            thumbnails.forEach(t => t.classList.remove("active"));
            // Добавляем текущему
            this.classList.add("active");
            mainImage.src = this.dataset.full;
        });
    });
});