function confirmDeleteProfile(btn) {
            // Проверяем, что кнопка нажата
            if (confirm("Вы уверены, что хотите удалить свой профиль? Все данные будут удалены, но комментарии останутся. Это действие нельзя отменить.")) {
                // Отправляем POST-запрос на удаление
                fetch("{% url 'users:delete_profile' %}", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": "{{ csrf_token }}", // передаём CSRF-токен
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({})
                })
                .then(response => {
                    if (response.ok) {
                        // Перенаправляем на logout
                        window.location.href = "{% url 'users:logout' %}";
                    } else {
                        alert("Ошибка при удалении профиля. Попробуйте снова.");
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("Ошибка при удалении профиля. Попробуйте снова.");
                });
            }
        }