(function () {
    document.addEventListener('DOMContentLoaded', function () {
        const form = document.querySelector('.comment-form');
        if (!form) return;

        const textInput = form.querySelector('[name="text"]');
        const parentInput = form.querySelector('[name="parent"]');
        const productId = form.getAttribute('data-product-id');
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        // === 1. Отправка комментария ===
        form.addEventListener('submit', handleSubmit);

        // === 2. Привязка кнопок "Ответить" и "Лайк" ===
        bindReplyButtons();
        bindLikeButtons();

        // === Функция: отправка формы ===
        async function handleSubmit(e) {
            e.preventDefault();

            if (!textInput.value.trim()) {
                alert('Введите текст комментария');
                return;
            }

            try {
                const formData = new FormData();
                formData.append('text', textInput.value);
                formData.append('parent', parentInput.value || '');
                formData.append('csrfmiddlewaretoken', csrfToken);

                const response = await fetch(`/product/${productId}/comment/create/`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Ошибка сервера:', errorText);
                    alert('Не удалось отправить комментарий');
                    return;
                }

                const comment = await response.json();
                console.log('✅ Комментарий создан:', comment);

                // Создаём HTML нового комментария
                const html = `
                <div class="comment-item" data-comment-id="${comment.id}" data-parent-id="${comment.parent_id || ''}">
                    <div class="comment-header">
                        <strong>${comment.user}</strong>
                        <span class="comment-date">${comment.created_at}</span>
                    </div>
                    <p class="comment-text">${comment.text}</p>
                    <div class="comment-actions">
                        <button class="like-btn">🤍 <span>0</span></button>
                        <button class="reply-btn" data-comment-id="${comment.id}">Ответить</button>
                    </div>
                    <div class="comment-avatar">
                        <img src="${comment.avatar}" alt="${comment.user}" width="40" height="40">
                    </div>
                    <div class="replies"></div>
                </div>
            `;

                const commentsList = document.getElementById('comments-list');
                if (!commentsList) {
                    console.error('❌ #comments-list не найден');
                    return;
                }

                if (comment.is_child) {
                    const parentEl = document.querySelector(`[data-comment-id="${comment.parent_id}"]`);
                    if (parentEl) {
                        const replies = parentEl.querySelector('.replies') || document.createElement('div');
                        replies.className = 'replies';
                        replies.insertAdjacentHTML('beforeend', commentHTML);
                        parentEl.appendChild(replies);
                    }
                } else {
                    commentsList.insertAdjacentHTML('beforeend', html);
                }

                // Сброс формы
                form.reset();
                parentInput.value = '';

                // Перепривязываем события
                bindReplyButtons();
                bindLikeButtons();

            } catch (error) {
                console.error('❌ Ошибка:', error);
                alert('Не удалось отправить комментарий');
            }
        }

        // === Функция: привязка кнопок "Ответить" ===
        function bindReplyButtons() {
            document.querySelectorAll('.reply-btn').forEach(btn => {
                btn.addEventListener('click', function () {
                    const commentId = this.getAttribute('data-comment-id');
                    const username = this.closest('.comment-item').querySelector('strong').textContent;
                    textInput.value = `${username}, `;
                    textInput.focus();
                    parentInput.value = commentId;
                });
            });
        }

        // === Функция: привязка кнопок "Лайк" ===
        function bindLikeButtons() {
            document.querySelectorAll('.like-btn').forEach(btn => {
                btn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    const span = this.querySelector('span');
                    let likes = parseInt(span.textContent) || 0;

                    if (!this.dataset.liked) {
                        likes++;
                        this.dataset.liked = 'true';
                        this.innerHTML = '❤️ <span>' + likes + '</span>';
                    } else {
                        likes = Math.max(0, likes - 1);
                        delete this.dataset.liked;
                        this.innerHTML = '🤍 <span>' + likes + '</span>';
                    }
                    span.textContent = likes;
                });
            });
        }
    });
})();
