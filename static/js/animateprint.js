document.addEventListener('DOMContentLoaded', function () {
    const text = 'Самая свежая техника — по лучшим ценам';
    const el = document.querySelector('.typewriter-text');
    let i = 0;

    // Эффект печати
    const typeWriter = () => {
        if (i < text.length) {
            el.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, 50); // Скорость печати (мс на символ)
        }
    };

    typeWriter();
});