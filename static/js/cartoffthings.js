document.addEventListener('DOMContentLoaded', function () {
    // Переключение миниатюр
    const thumbs = document.querySelectorAll('.thumb');
    const mainImage = document.querySelector('.main-image');

    thumbs.forEach(thumb => {
        thumb.addEventListener('click', function () {
            // Удаляем активный класс у всех
            thumbs.forEach(t => t.classList.remove('active'));
            // Добавляем текущему
            this.classList.add('active');
            // Меняем главное изображение
            mainImage.src = this.src;
        });
    });

    // Управление количеством
    const minusBtn = document.querySelector('.qty-btn.minus');
    const plusBtn = document.querySelector('.qty-btn.plus');
    const quantity = document.querySelector('.quantity');

    minusBtn.addEventListener('click', () => {
        let qty = parseInt(quantity.textContent);
        if (qty > 1) {
            qty--;
            quantity.textContent = qty;
        }
    });

    plusBtn.addEventListener('click', () => {
        let qty = parseInt(quantity.textContent);
        qty++;
        quantity.textContent = qty;
    });

    // Добавление в корзину
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    addToCartBtn.addEventListener('click', function () {
        const productName = document.querySelector('.product-title').textContent;
        alert(`Товар "${productName}" добавлен в корзину!`);
    });

    // Лайк / Избранное
    const likeBtn = document.querySelector('.like-btn');
    likeBtn.addEventListener('click', function () {
        this.innerHTML = this.innerHTML.includes('❤️') ? '🤍' : '❤️';
        const action = this.innerHTML.includes('❤️') ? 'добавлен в избранное' : 'удалён из избранного';
        const productName = document.querySelector('.product-title').textContent;
        alert(`Товар "${productName}" ${action}`);
    });
});