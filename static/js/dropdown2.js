// static/js/dropdown2.js

document.addEventListener('DOMContentLoaded', function () {
    // Закрываем все .dropdown2, кроме одного
    function closeAllDropdowns(except) {
        document.querySelectorAll('.dropdown2').forEach(dropdown => {
            if (dropdown !== except) {
                dropdown.classList.remove('open');
            }
        });
    }

    // Обрабатываем каждое меню .dropdown2
    document.querySelectorAll('.dropdown2').forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (!toggle) return;

        // Клик по кнопке — открывает/закрывает
        toggle.addEventListener('click', (e) => {
            e.preventDefault(); // Не переходим по #
            const isOpen = dropdown.classList.toggle('open');

            if (isOpen) {
                closeAllDropdowns(dropdown); // Только одно открыто
            }
        });
    });

    // Закрытие при клике вне
    document.addEventListener('click', (e) => {
        document.querySelectorAll('.dropdown2').forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    });

    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.dropdown2').forEach(dropdown => {
                dropdown.classList.remove('open');
            });
        }
    });
});