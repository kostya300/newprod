// static/js/radio.js

document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('radio-audio');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    const prevStationBtn = document.getElementById('prev-station-btn');
    const nextStationBtn = document.getElementById('next-station-btn');
    const volumeSlider = document.getElementById('volume-slider');
    const muteBtn = document.getElementById('mute-btn');
    const stationName = document.getElementById('station-name');
    const stationCover = document.getElementById('station-cover');
    const timerProgress = document.getElementById('timer-progress');
    const status = document.getElementById('status');
    const stationsMenu = document.getElementById('stations-menu');

    let progressInterval = null;
    let isMuted = false;
    let currentKey = null;

    const stations = window.radioStations;

    const keys = Object.keys(stations);

    // Восстановление последней станции
    const lastStation = localStorage.getItem('lastRadioStation') || 'retro';
    if (stations[lastStation]) {
        currentKey = lastStation;
        loadStation(lastStation);
        setActiveStation(lastStation);
    }

    // === Функции ===

    function loadStation(key) {
        if (!stations[key]) return;
        if (!audio.paused) audio.pause();

        const station = stations[key];
        stationName.textContent = station.name;
        stationCover.src = station.cover;
        status.textContent = 'Готово';

        audio.src = station.stream;
        audio.volume = volumeSlider.value;
        audio.load();

        playPauseBtn.disabled = false;
        currentKey = key;
        localStorage.setItem('lastRadioStation', key);
        setActiveStation(key);
    }

    function setActiveStation(key) {
        document.querySelectorAll('#stations-menu li').forEach(li => {
            li.classList.remove('active');
        });
        const active = document.querySelector(`#stations-menu li[data-key="${key}"]`);
        if (active) active.classList.add('active');
    }

    function startProgress() {
        timerProgress.style.width = '20%';
        progressInterval = setInterval(() => {
            const width = parseInt(timerProgress.style.width) || 0;
            timerProgress.style.width = width >= 100 ? '0%' : (width + 1) + '%';
        }, 200);
    }

    function pauseProgress() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }

    // === Динамическая заливка ползунка громкости ===
    function updateVolumeSlider() {
        const value = volumeSlider.value;
        const max = volumeSlider.max;
        const percent = (value / max) * 100;

        volumeSlider.style.background = `
            linear-gradient(
                to right,
                var(--accent-color, #6e8efb) 0%,
                var(--accent-color, #6e8efb) ${percent}%,
                #ddd ${percent}%,
                #ddd 100%
            )
        `;
    }

    // Инициализация ползунка
    updateVolumeSlider();

    // === Переключение станций ===
    prevStationBtn.addEventListener('click', () => {
        const index = keys.indexOf(currentKey);
        const prev = keys[(index - 1 + keys.length) % keys.length];
        loadStation(prev);
    });

    nextStationBtn.addEventListener('click', () => {
        const index = keys.indexOf(currentKey);
        const next = keys[(index + 1) % keys.length];
        loadStation(next);
    });

    // === Список станций ===
    document.querySelectorAll('#stations-menu li').forEach(li => {
        li.addEventListener('click', () => {
            const key = li.dataset.key;
            if (key !== currentKey) loadStation(key);
        });
    });

    // === Воспроизведение ===
    playPauseBtn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().then(() => {
                playPauseBtn.className = 'fas fa-pause-circle';
                status.textContent = 'В эфире...';
                startProgress();
            }).catch(err => {
                alert('Разрешите автовоспроизведение');
                status.textContent = 'Блокировка';
            });
        } else {
            audio.pause();
            playPauseBtn.className = 'fas fa-play-circle';
            status.textContent = 'На паузе';
            pauseProgress();
        }
    });

    stopBtn.addEventListener('click', () => {
        audio.pause();
        audio.currentTime = 0;
        playPauseBtn.className = 'fas fa-play-circle';
        status.textContent = 'Оффлайн';
        pauseProgress();
        timerProgress.style.width = '0%';
    });

    // === Громкость ===
    volumeSlider.addEventListener('input', () => {
        audio.volume = volumeSlider.value;
        isMuted = false;
        muteBtn.className = 'fas fa-volume-up';
        muteBtn.classList.remove('muted');
        updateVolumeSlider(); // Обновляем фон
    });

    muteBtn.addEventListener('click', () => {
        if (isMuted) {
            audio.volume = volumeSlider.value;
            muteBtn.className = 'fas fa-volume-up';
            muteBtn.classList.remove('muted');
        } else {
            audio.volume = 0;
            muteBtn.className = 'fas fa-volume-mute';
            muteBtn.classList.add('muted');
        }
        isMuted = !isMuted;
        updateVolumeSlider(); // Чтобы фон не "завис"
    });

    // === События аудио ===
    audio.addEventListener('error', () => {
        status.textContent = '🔴 Ошибка подключения';
        pauseProgress();
    });

    audio.addEventListener('playing', () => {
        status.textContent = 'В эфире...';
    });

    audio.addEventListener('pause', () => {
        if (!audio.ended) status.textContent = 'На паузе';
    });
});