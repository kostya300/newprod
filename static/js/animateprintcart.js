document.addEventListener('DOMContentLoaded', function () {
    const text = 'Проверьте и оформите свой заказ';
    const el = document.querySelector('.typewriter-text');
    let i = 0;

    // Эффект печати
    const typeWriter = () => {
        if (i < text.length) {
            el.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, 70); // Скорость печати (мс на символ)
        }
    };

    typeWriter();
});