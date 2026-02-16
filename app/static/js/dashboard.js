// dashboard.js

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Fetch Dashboard Stats
    try {
        const response = await fetch('/ui/api/dashboard-stats');
        const data = await response.json();

        // Update Stats Cards
        document.getElementById('stats-total').textContent = data.total_scans;
        document.getElementById('stats-running').textContent = data.running_scans;
        document.getElementById('stats-avg-risk').textContent = data.avg_risk.toFixed(1);
        document.getElementById('stats-critical').textContent = data.critical_findings;

        // Update Charts
        renderRiskTrendChart(data.risk_history);
        renderSeverityChart(data.severity_distribution);

        // Update Recent Scans
        updateRecentScansTable(data.recent_scans);

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
});

function renderRiskTrendChart(history) {
    const ctx = document.getElementById('riskTrendChart').getContext('2d');

    // Sort by date
    history.sort((a, b) => new Date(a.date) - new Date(b.date));

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(h => new Date(h.date).toLocaleDateString()),
            datasets: [{
                label: 'Average Risk Score',
                data: history.map(h => h.risk_score),
                borderColor: '#60a5fa',
                backgroundColor: 'rgba(96, 165, 250, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#2563eb',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: { mode: 'index', intersect: false }
            }
        }
    });
}

function renderSeverityChart(distribution) {
    const ctx = document.getElementById('severityPieChart').getContext('2d');

    const labels = ['Critical', 'High', 'Medium', 'Low', 'Info'];
    const data = [
        distribution.critical || 0,
        distribution.high || 0,
        distribution.medium || 0,
        distribution.low || 0,
        distribution.info || 0
    ];

    createDoughnutChart(ctx, labels, data, [
        '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'
    ]);
}

function updateRecentScansTable(scans) {
    const tbody = document.getElementById('recent-scans-body');
    tbody.innerHTML = '';

    if (scans.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No scans found</td></tr>`;
        return;
    }

    scans.forEach(scan => {
        const row = document.createElement('tr');

        let statusClass = 'badge-completed';
        if (scan.status === 'running') statusClass = 'badge-running';
        if (scan.status === 'failed') statusClass = 'badge-failed';
        if (scan.status === 'timeout') statusClass = 'badge-timeout';

        let riskColor = '#22c55e';
        if (scan.risk_score >= 8) riskColor = '#ef4444';
        else if (scan.risk_score >= 6) riskColor = '#f97316';
        else if (scan.risk_score >= 4) riskColor = '#eab308';

        row.innerHTML = `
            <td><a href="/scan/${scan.scan_id}" style="font-weight: 500; color: #e2e8f0;">${scan.target}</a></td>
            <td><span class="badge ${statusClass}">${scan.status}</span></td>
            <td><span style="color: ${riskColor}; font-weight: bold;">${scan.risk_score.toFixed(1)}</span></td>
            <td style="color: var(--text-muted); font-size: 0.85rem;">${new Date(scan.created_at).toLocaleString()}</td>
            <td>
                <a href="/scan/${scan.scan_id}" class="btn btn-sm btn-outline">
                    View <i class="fa-solid fa-arrow-right" style="margin-left: 4px;"></i>
                </a>
            </td>
        `;
        tbody.appendChild(row);
    });
}
