const scanId = window.location.pathname.split('/').pop();

document.addEventListener('DOMContentLoaded', async () => {
    // Buttons
    document.getElementById('retry-btn').onclick = () => retryScan();
    document.getElementById('delete-btn').onclick = () => deleteScan();
    document.getElementById('json-toggle').onclick = () => toggleJson();

    try {
        const res = await fetch(`/api/scan/results/${scanId}`);
        if (!res.ok) throw new Error('Failed to fetch scan details');

        const data = await res.json();
        renderDetail(data);

        // Auto refresh if running
        if (data.status === 'running') {
            setTimeout(() => window.location.reload(), 5000);
        }
    } catch (err) {
        console.error(err);
        document.getElementById('findings-list').innerHTML = `
            <div class="text-center text-red-500 py-4">Error loading scan details</div>
        `;
    }
});

function renderDetail(data) {
    // Header Info
    document.getElementById('target-name').textContent = data.target;
    document.getElementById('scan-id').textContent = data.scan_id;
    document.getElementById('scan-time').textContent = new Date(data.created_at).toLocaleString();
    document.getElementById('scan-duration').textContent = data.duration ? `${data.duration.toFixed(1)}s` : '---';

    // Status Badge
    const statusBadge = document.getElementById('scan-status-badge');
    statusBadge.textContent = data.status;
    statusBadge.className = `badge badge-${data.status}`;

    // Risk Score
    const riskCircle = document.getElementById('risk-circle');
    riskCircle.textContent = data.risk_score.toFixed(1);

    let riskColor = 'var(--success)';
    if (data.risk_score >= 8) riskColor = 'var(--danger)';
    else if (data.risk_score >= 6) riskColor = '#f97316';
    else if (data.risk_score >= 4) riskColor = 'var(--warning)';

    riskCircle.style.borderColor = riskColor;
    riskCircle.style.color = riskColor;

    // Charts
    const ctx = document.getElementById('detailChart').getContext('2d');
    const severity = data.summary?.severity_distribution || {};

    createDoughnutChart(ctx,
        Object.keys(severity).map(k => k.toUpperCase()),
        Object.values(severity),
        Object.keys(severity).map(k => {
            if (k === 'critical') return '#ef4444';
            if (k === 'high') return '#f97316';
            if (k === 'medium') return '#eab308';
            if (k === 'low') return '#22c55e';
            return '#3b82f6';
        })
    );

    // Vulnerabilities List
    const list = document.getElementById('findings-list');
    list.innerHTML = '';

    const vulns = data.nuclei?.vulnerabilities || [];
    if (vulns.length === 0) {
        list.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No vulnerabilities found.</div>`;
    } else {
        vulns.forEach(v => {
            const card = document.createElement('div');
            card.className = 'finding-card';

            let badgeClass = 'bg-gray-100 text-gray-800';
            if (v.severity === 'critical') badgeClass = 'badge-failed'; // red
            if (v.severity === 'high') badgeClass = 'badge-failed'; // orange-red
            if (v.severity === 'medium') badgeClass = 'badge-timeout'; // yellow
            if (v.severity === 'low') badgeClass = 'badge-completed'; // green

            card.innerHTML = `
                <div class="finding-header" onclick="this.nextElementSibling.classList.toggle('open')">
                    <div class="finding-title">
                        <span class="badge ${badgeClass}">${v.severity}</span>
                        <span>${v.name || 'Unknown Vulnerability'}</span>
                    </div>
                    <i class="fa-solid fa-chevron-down" style="color: var(--text-muted);"></i>
                </div>
                <div class="finding-details">
                    <p style="margin-bottom: 0.5rem;"><strong>Description:</strong> ${v.description || 'No description available.'}</p>
                    <p style="margin-bottom: 0.5rem;"><strong>Template ID:</strong> ${v.template_id}</p>
                    <p style="margin-bottom: 0.5rem;"><strong>Matcher:</strong> ${v.matcher_name || 'N/A'}</p>
                    <div style="margin-top: 1rem;">
                        <strong>References:</strong>
                        <ul style="list-style: disc; margin-left: 1.5rem; margin-top: 0.5rem; color: var(--primary);">
                            ${(v.references || []).map(ref => `<li><a href="${ref}" target="_blank">${ref}</a></li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            list.appendChild(card);
        });
    }

    // Open Ports
    const portsContainer = document.getElementById('ports-list');
    const ports = data.nmap?.ports || [];

    if (ports.length > 0) {
        document.getElementById('port-count').textContent = ports.length;
        portsContainer.innerHTML = '';
        ports.forEach(p => {
            const portBadge = document.createElement('span');
            portBadge.className = 'badge badge-completed'; // green
            portBadge.style.marginRight = '0.5rem';
            portBadge.style.marginBottom = '0.5rem';
            portBadge.innerHTML = `<i class="fa-solid fa-plug" style="margin-right: 4px;"></i> ${p.port}/${p.protocol} (${p.service || 'unknown'})`;
            portsContainer.appendChild(portBadge);
        });
    }

    // JSON Raw View
    document.getElementById('json-content').textContent = JSON.stringify(data, null, 2);
}

function toggleJson() {
    const view = document.getElementById('json-view');
    view.style.display = view.style.display === 'none' ? 'block' : 'none';
}

async function retryScan() {
    try {
        const res = await fetch(`/api/scan/${scanId}/retry`, { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            window.location.href = `/scan/${data.scan_id}`; // Redirect to new scan
        } else {
            alert('Retry failed');
        }
    } catch (e) {
        console.error(e);
        alert('Error initiating retry');
    }
}

async function deleteScan() {
    if (!confirm('Delete this scan? This cannot be undone.')) return;
    try {
        const res = await fetch(`/api/scan/${scanId}`, { method: 'DELETE' });
        if (res.ok) {
            window.location.href = '/history';
        } else {
            alert('Delete failed');
        }
    } catch (e) {
        console.error(e);
    }
}
