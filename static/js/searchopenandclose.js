// Открыть и закрыть модальный поиск
const openSearchBtn = document.getElementById('open-search-btn');
const closeSearchBtn = document.getElementById('close-search');
const searchModal = document.getElementById('search-modal');

openSearchBtn?.addEventListener('click', () => {
    searchModal.style.display = 'flex';
});

closeSearchBtn?.addEventListener('click', () => {
    searchModal.style.display = 'none';
});

// Закрытие по Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        searchModal.style.display = 'none';
    }
});