// static/js/goodsforinternet.js

async function searchProducts() {
    const query = document.getElementById('user-query').value.trim();
    if (!query) {
        alert('Введите запрос');
        return;
    }

    const resultsContainer = document.getElementById('ai-results');
    const loading = document.getElementById('loading');

    loading.style.display = 'block';
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch('/api/ai-internet-goods/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.products && data.products.length > 0) {
            renderProductCards(data.products);
        } else {
            resultsContainer.innerHTML = '<p>Товары не найдены. Попробуйте уточнить запрос.</p>';
        }
    } catch (error) {
        resultsContainer.innerHTML = '<p>Ошибка при поиске. Попробуйте позже.</p>';
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
function renderProductCards(products) {
    const container = document.getElementById('ai-results');
    container.innerHTML = ''; // очищаем

    products.forEach(product => {
        let imgSrc = product.image;

        if (!imgSrc || typeof imgSrc !== 'string' || imgSrc.trim() === '') {
            imgSrc = 'https://picsum.photos/300/200';
        } else {
            imgSrc = imgSrc.trim();
            if (imgSrc.startsWith('//')) {
                imgSrc = 'https:' + imgSrc;
            } else if (!imgSrc.startsWith('http://') && !imgSrc.startsWith('https://')) {
                imgSrc = 'https://picsum.photos/300/200';
            }
        }

        try {
            new URL(imgSrc);
        } catch (e) {
            imgSrc = 'https://picsum.photos/300/200';
        }

        const card = document.createElement('div');
        card.className = 'ai-product-card';

        card.innerHTML = `
            <img src="${imgSrc}" 
                 alt="${escapeHtml(product.name)}"
                 onerror="this.onerror=null; this.src='https://picsum.photos/300/200';">

            <div class="ai-product-info">
                <h3 class="product-title">${escapeHtml(product.name)}</h3>
                <div class="product-price">${product.price} ₽</div>
                <p class="product-desc"><small>Магазин: <strong>${escapeHtml(product.store || 'Неизвестно')}</strong></small></p>
                <a href="${product.url}" target="_blank" class="action-btn" onclick="event.stopPropagation();">
                    Перейти ↗
                </a>
            </div>
        `;

        container.appendChild(card);
    });
}

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