document.addEventListener('DOMContentLoaded', function () {
    const commentsList = document.querySelector('.comments-list');
    const addComment = document.querySelector('.add-comment');
    const textarea = addComment?.querySelector('textarea');
    const submitBtn = addComment?.querySelector('.submit-comment');

    // Лайки
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const span = this.querySelector('span');
            let likes = parseInt(span.textContent);
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

    // Ответить
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const commentItem = this.closest('.comment-item');
            const isReplying = commentItem.classList.contains('reply-mode');

            // Убираем все режимы
            document.querySelectorAll('.comment-item').forEach(el => {
                el.classList.remove('reply-mode');
            });

            if (!isReplying) {
                const replyForm = document.createElement('div');
                replyForm.className = 'add-comment';
                replyForm.style.marginTop = '16px';
                replyForm.innerHTML = `
                    <textarea placeholder="Напишите ответ..."></textarea>
                    <button class="submit-comment">Отправить</button>
                `;
                commentItem.appendChild(replyForm);
                commentItem.classList.add('reply-mode');

                replyForm.querySelector('.submit-comment').addEventListener('click', function () {
                    const text = replyForm.querySelector('textarea').value.trim();
                    if (text) {
                        const replyItem = document.createElement('div');
                        replyItem.className = 'comment-item reply';
                        replyItem.innerHTML = `
                            <div class="comment-header">
                                <strong>Вы</strong>
                                <span class="comment-date">Сейчас</span>
                            </div>
                            <p class="comment-text">${text}</p>
                            <div class="comment-actions">
                                <button class="like-btn">❤️ <span>0</span></button>
                            </div>
                        `;
                        commentItem.querySelector('.replies')?.appendChild(replyItem);
                        replyForm.remove();
                        commentItem.classList.remove('reply-mode');

                        // Добавляем лайк-обработчик
                        replyItem.querySelector('.like-btn').addEventListener('click', function (e) {
                            e.stopPropagation();
                            const span = this.querySelector('span');
                            let likes = parseInt(span.textContent);
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
                    }
                });
            }
        });
    });

    // Отправка нового отзыва
    submitBtn?.addEventListener('click', function () {
        const text = textarea.value.trim();
        if (text) {
            const newComment = document.createElement('div');
            newComment.className = 'comment-item';
            newComment.innerHTML = `
                <div class="comment-header">
                    <strong>Вы</strong>
                    <span class="comment-date">Сейчас</span>
                </div>
                <p class="comment-text">${text}</p>
                <div class="comment-actions">
                    <button class="like-btn">❤️ <span>0</span></button>
                    <button class="reply-btn">Ответить</button>
                </div>
                <div class="replies"></div>
            `;
            commentsList.prepend(newComment);
            textarea.value = '';

            // Назначаем обработчики
            newComment.querySelector('.like-btn').addEventListener('click', function (e) {
                e.stopPropagation();
                const span = this.querySelector('span');
                let likes = parseInt(span.textContent);
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

            newComment.querySelector('.reply-btn').addEventListener('click', function () {
                // То же поведение, что и выше
            });
        }
    });
});