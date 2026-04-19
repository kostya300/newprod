document.addEventListener('DOMContentLoaded', function () {
    const cartItems = document.querySelectorAll('.cart-item');
    const totalAmount = document.getElementById('total-amount');
    const deliveryRadios = document.querySelectorAll('input[name="delivery"]');

    // Функция пересчёта итога
    function updateTotal() {
        let total = 0;
        cartItems.forEach(item => {
            const priceText = item.querySelector('.item-price').textContent.replace(' ₽', '').replace(/\s+/g, '');
            const price = parseInt(priceText);
            const quantity = parseInt(item.querySelector('.quantity').textContent);
            total += price * quantity;
        });

        // Добавляем стоимость доставки
        const selectedDelivery = document.querySelector('input[name="delivery"]:checked');
        if (selectedDelivery?.value === 'courier') total += 300;
        if (selectedDelivery?.value === 'post') total += 200;

        totalAmount.textContent = total.toLocaleString() + ' ₽';
    }

    // Кнопки изменения количества
    cartItems.forEach(item => {
        const minusBtn = item.querySelector('.minus');
        const plusBtn = item.querySelector('.plus');
        const qtySpan = item.querySelector('.quantity');

        minusBtn.addEventListener('click', () => {
            let qty = parseInt(qtySpan.textContent);
            if (qty > 1) {
                qty--;
                qtySpan.textContent = qty;
                updateTotal();
            }
        });

        plusBtn.addEventListener('click', () => {
            let qty = parseInt(qtySpan.textContent);
            qty++;
            qtySpan.textContent = qty;
            updateTotal();
        });

        // Удаление товара
        const removeBtn = item.querySelector('.remove-btn');
        removeBtn.addEventListener('click', () => {
            item.remove();
            updateTotal();
        });
    });

    // Обновление итога при изменении доставки
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', updateTotal);
    });

    // Кнопка оплаты
    const checkoutBtn = document.querySelector('.checkout-btn');
    checkoutBtn?.addEventListener('click', () => {
        const fullname = document.getElementById('fullname').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const email = document.getElementById('email').value.trim();

        if (!fullname || !phone || !email) {
            alert('Пожалуйста, заполните все обязательные поля.');
            return;
        }

        alert('Спасибо за заказ! Он будет оформлен и отправлен на проверку.');
    });

    // Инициализация общей суммы
    updateTotal();
});