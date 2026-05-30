document.addEventListener('DOMContentLoaded', function () {
    const chat = document.getElementById('support-chat');
    const toggle = document.getElementById('support-chat-toggle');
    const minimize = document.getElementById('support-chat-minimize');
    const close = document.getElementById('support-chat-close');
    const body = document.getElementById('support-chat-body');
    const input = document.getElementById('support-chat-input');
    const send = document.getElementById('support-chat-send');

    // Открыть/закрыть
    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        chat.classList.toggle('open');
        if (chat.classList.contains('open')) {
            chat.classList.remove('minimized');
        }
    });

    // Свернуть
    minimize.addEventListener('click', () => {
        chat.classList.toggle('minimized');
    });

    // Закрыть
    close.addEventListener('click', () => {
        chat.classList.remove('open');
    });

    // Отправка сообщения
    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // Пользователь
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.textContent = text;
        body.appendChild(userMsg);

        input.value = '';

        // Прокрутка вниз
        body.scrollTop = body.scrollHeight;

        // Бот отвечает через 0.5 сек
        setTimeout(() => {
            const botMsg = document.createElement('div');
            botMsg.className = 'message bot';
            botMsg.innerHTML = '<strong>Техподдержка:</strong><br>Спасибо за сообщение! Мы ответим в течение 24 часов.';
            body.appendChild(botMsg);
            body.scrollTop = body.scrollHeight;
        }, 500);
    }

    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
