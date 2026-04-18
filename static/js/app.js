// Theme toggle with localStorage persistence
(function() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    function getTheme() {
        return localStorage.getItem('theme') || 'light';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updatePlotlyTheme(theme);
    }

    toggle.addEventListener('click', () => {
        const current = getTheme();
        setTheme(current === 'light' ? 'dark' : 'light');
    });

    // Update Plotly charts when theme changes
    function updatePlotlyTheme(theme) {
        const isDark = theme === 'dark';
        const plotContainers = document.querySelectorAll('.chart-container .js-plotly-plot');
        plotContainers.forEach(el => {
            if (typeof Plotly !== 'undefined') {
                Plotly.relayout(el, {
                    paper_bgcolor: isDark ? '#1e293b' : '#ffffff',
                    plot_bgcolor: isDark ? '#1e293b' : '#ffffff',
                    font: { color: isDark ? '#e2e8f0' : '#1e293b' },
                    xaxis: { gridcolor: isDark ? '#334155' : '#e2e8f0', color: isDark ? '#e2e8f0' : '#1e293b' },
                    yaxis: { gridcolor: isDark ? '#334155' : '#e2e8f0', color: isDark ? '#e2e8f0' : '#1e293b' },
                });
            }
        });
    }

    // Apply to any charts already rendered
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => updatePlotlyTheme(getTheme()), 500);
    });
})();

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
