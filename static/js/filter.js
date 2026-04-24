// static/js/filter.js (или desktopfilter.js)

function closeFilterDropdown() {
    document.getElementById('header-filter-dropdown').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('open-filter-btn');
    const dropdown = document.getElementById('header-filter-dropdown');

    if (!btn || !dropdown) return;

    btn.addEventListener('click', function (e) {
        if (window.innerWidth <= 768) return;
        e.preventDefault();
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function (e) {
        if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
});