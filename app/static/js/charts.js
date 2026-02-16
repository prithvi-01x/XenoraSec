// charts.js
// Shared Chart.js configuration

const chartColors = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
    info: '#3b82f6',
    background: '#1e293b'
};

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                color: '#94a3b8',
                font: {
                    family: 'Inter',
                    size: 11
                },
                usePointStyle: true,
                padding: 20
            }
        },
        tooltip: {
            backgroundColor: '#1f2937',
            titleColor: '#f9fafb',
            bodyColor: '#e5e7eb',
            borderColor: '#374151',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 4,
            displayColors: true
        }
    },
    scales: {
        x: {
            grid: {
                color: '#334155',
                drawBorder: false
            },
            ticks: {
                color: '#94a3b8'
            }
        },
        y: {
            grid: {
                color: '#334155',
                drawBorder: false
            },
            ticks: {
                color: '#94a3b8',
                stepSize: 1
            },
            beginAtZero: true
        }
    }
};

function createDoughnutChart(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            ...commonOptions,
            cutout: '70%',
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}
