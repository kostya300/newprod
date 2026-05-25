// static/js/delcomment.js

// Убедитесь, что getCSRFToken доступна глобально
// (она должна быть определена в шаблоне, см. ниже)
if (typeof window.getCSRFToken !== 'function') {
    console.error('Функция getCSRFToken не найдена. Убедитесь, что она определена в шаблоне.');
}

// Привязка при загрузке и после добавления комментария
document.addEventListener('DOMContentLoaded', bindDeleteButtons);
document.addEventListener('commentAdded', bindDeleteButtons);

function bindDeleteButtons() {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.removeEventListener('click', handleDeleteClick);
        btn.addEventListener('click', handleDeleteClick);
    });
}

async function handleDeleteClick(e) {
    const btn = e.currentTarget;
    const commentId = btn.getAttribute('data-comment-id');

    if (!commentId) {
        console.error('У кнопки удаления нет data-comment-id');
        return;
    }

    if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) {
        return;
    }

    try {
        const response = await fetch(`/comment/${commentId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `Ошибка: ${response.status}`);
        }

        const commentEl = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (commentEl) {
            commentEl.style.opacity = '0';
            commentEl.style.transition = 'opacity 0.3s ease';
            setTimeout(() => commentEl.remove(), 300);
        }

        alert('Комментарий удалён');
    } catch (error) {
        console.error('Ошибка удаления:', error);
        alert('Не удалось удалить комментарий: ' + (error.message || 'неизвестная ошибка'));
    }
}