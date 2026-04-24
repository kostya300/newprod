// static/js/ai-assistant.js

document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('ai-toggle-btn');
    const chatWindow = document.getElementById('ai-chat-window');
    const closeBtn = document.getElementById('ai-close-btn');
    const fullscreenBtn = document.getElementById('ai-fullscreen-btn');
    const messagesDiv = document.getElementById('ai-messages');
    const input = document.getElementById('ai-input');
    const sendBtn = document.getElementById('ai-send-btn');

    // Иконки SVG
    const fullscreenIconExpand = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M3 3h8v2H5v6H3V3z"/>
            <path d="M21 3h-8v2h6v6h2V3z"/>
            <path d="M21 21h-8v-2h6v-6h2v8z"/>
            <path d="M3 21h8v-2H5v-6H3v8z"/>
        </svg>
    `;

    const fullscreenIconCollapse = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11v-3h-2v5h5v-2h-3z"/>
        </svg>
    `;

    // === Обработчики событий ===

    // Открыть/закрыть окно
    toggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('show');
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.remove('show');
    });

    // Переключение полноэкранного режима
    fullscreenBtn.innerHTML = fullscreenIconExpand;

    fullscreenBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('fullscreen');
        if (chatWindow.classList.contains('fullscreen')) {
            fullscreenBtn.innerHTML = fullscreenIconCollapse;
        } else {
            fullscreenBtn.innerHTML = fullscreenIconExpand;
        }
    });

    // Отправка сообщения
    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        appendMessage('<strong>Вы:</strong> ' + text, 'user');
        input.value = '';

        const typing = document.createElement('p');
        typing.innerHTML = '<strong>🤖:</strong> Думаю...';
        messagesDiv.appendChild(typing);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        fetch('/api/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ message: text }),
        })
        .then(response => response.json())
        .then(data => {
            messagesDiv.removeChild(typing);
            appendMessage('<strong>🤖:</strong> ' + data.response, 'ai');
        })
        .catch(err => {
            messagesDiv.removeChild(typing);
            appendMessage('<strong>🤖:</strong> Ошибка подключения.', 'ai');
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    // === Добавление сообщения с поддержкой кода ===
    function appendMessage(text, sender) {
    const p = document.createElement('p');

    // Преобразуем Markdown-подобный текст в HTML
    let html = text
        // Заголовки ### → <h5>
        .replace(/###\s*(.+?)\n/g, '<h5 class="ai-msg-heading">$1</h5>')
        // Жирный шрифт **текст** → <strong>
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Маркированный список - → <ul><li>
        .replace(/(?:^|\n)-\s+(.+?)(?=\n-|\n\n|$)/g, (match, item) =>
            `<li>${item}</li>`
        )
        // Оборачиваем списки в <ul>
        .replace(/((<li>.+?<\/li>\s*)+)/g, '<ul class="ai-msg-list">$1</ul>');

    p.innerHTML = html;
    messagesDiv.appendChild(p);

    // Подсветка кода
    if (p.querySelector('pre code')) {
        hljs.highlightAll();
    }

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
    // === Экранирование HTML ===
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    // === CSRF токен ===
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});