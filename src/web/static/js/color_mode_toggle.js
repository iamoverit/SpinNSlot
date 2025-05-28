function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;
    
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlEl.setAttribute('data-bs-theme', savedTheme);
    
    themeToggle.querySelector('i').className = savedTheme === 'dark' 
        ? 'bi bi-moon-fill' 
        : 'bi bi-sun-fill';

    themeToggle.addEventListener('click', () => {
        const isDark = htmlEl.getAttribute('data-bs-theme') === 'dark';
        const newTheme = isDark ? 'light' : 'dark';

        fetch('/user/set-theme/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `theme=${newTheme}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                htmlEl.setAttribute('data-bs-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                themeToggle.querySelector('i').className = isDark 
                    ? 'bi bi-sun-fill' 
                    : 'bi bi-moon-fill';
            }
        });
    });
});