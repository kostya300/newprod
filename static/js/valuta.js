// static/js/valuta.js

// Список валют
const currencies = [
    { code: 'USD', name: 'Доллар США' },
    { code: 'EUR', name: 'Евро' },
    { code: 'KZT', name: 'Тенге' },
    { code: 'CNY', name: 'Юань' }
];

// Форматтер для чисел (2 знака после запятой, с разделителями)
// Глобальная переменная — один раз
const formatter = new Intl.NumberFormat('ru-RU', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

// Генерация "истории" курса за 30 дней (для демо)
function generateMockHistory(baseRate) {
    const history = [];
    let rate = baseRate;
    for (let i = 0; i < 31; i++) {
        const change = rate * (Math.random() * 0.04 - 0.02); // ±2%
        rate = Math.max(rate + change, 0.1);
        history.push(parseFloat(rate.toFixed(2)));
    }
    return history;
}

// Создание мини-графика
function createMiniChart(ctx, data, code) {
    const dates = [];
    const today = new Date();
    for (let i = 30; i >= 0; i--) {
        const d = new Date(today);
        d.setDate(today.getDate() - i);
        const day = d.getDate().toString().padStart(2, '0');
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        dates.push(`${day}.${month}`);
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `Курс ${code}`,
                data: data,
                borderColor: '#6e8efb',
                backgroundColor: 'rgba(110, 142, 251, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    displayColors: false,
                    padding: 10,
                    cornerRadius: 6,
                    callbacks: {
                        title: (context) => `${context[0].label} (${context[0].dataset.label})`,
                        label: (context) => `Курс: ${context.parsed.y} ₽`
                    }
                },
                legend: { display: false }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    display: true,
                    grid: { display: false },
                    ticks: { display: false }
                },
                y: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Загрузка данных
async function loadCurrency() {
    try {
        const response = await fetch('https://www.cbr-xml-daily.ru/latest.js');
        const data = await response.json();

        const usdToRub = data.rates.RUB;
        const eurToRub = data.rates.EUR;
        const cnyToRub = data.rates.CNY;
        const kztToRub = data.rates.KZT;

        const rates = {
            USD: usdToRub,
            EUR: eurToRub || usdToRub * 1.08,
            CNY: cnyToRub,
            KZT: kztToRub
        };

        console.log('Курсы (RUB):', rates);

        const container = document.getElementById('currency-grid');
        container.innerHTML = '';

        currencies.forEach(curr => {
            const rate = rates[curr.code];

            if (!rate || isNaN(rate)) {
                console.warn(`Курс для ${curr.code} недоступен`);
                return;
            }

            const formattedRate = formatter.format(rate); // ✅ Используем глобальный formatter

            const card = document.createElement('div');
            card.className = 'currency-card';
            card.innerHTML = `
                <div class="currency-code">${curr.code}</div>
                <div class="currency-rate">${formattedRate} ₽</div>
                <div class="mini-chart">
                    <canvas class="chart-canvas"></canvas>
                </div>
            `;
            container.appendChild(card);

            const ctx = card.querySelector('.chart-canvas').getContext('2d');
            createMiniChart(ctx, generateMockHistory(rate), curr.code);
        });

    } catch (err) {
        console.error('Ошибка загрузки курсов:', err);
        document.getElementById('currency-grid').innerHTML = `
            <p style="color: red">Ошибка подключения к API</p>
        `;
    }
}

document.addEventListener('DOMContentLoaded', loadCurrency);