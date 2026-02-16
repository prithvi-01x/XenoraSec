let currentPage = 1;
const ITEMS_PER_PAGE = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadHistory(1);

    // Add event listeners for filters
    document.getElementById('status-filter').addEventListener('change', () => loadHistory(1));
    document.getElementById('search-input').addEventListener('input', debounce(() => loadHistory(1), 500));
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function loadHistory(page) {
    currentPage = page;
    const offset = (page - 1) * ITEMS_PER_PAGE;

    const status = document.getElementById('status-filter').value;
    const search = document.getElementById('search-input').value;

    let url = `/api/scan/history?limit=${ITEMS_PER_PAGE}&offset=${offset}`;
    if (status) url += `&status=${status}`;
    if (search) url += `&target=${search}`;

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch history');

        const data = await res.json();
        renderTable(data.items);
        renderPagination(data.total, page);

    } catch (err) {
        console.error(err);
        document.getElementById('history-body').innerHTML = `
            <tr><td colspan="6" class="text-center text-red-500">Error loading data</td></tr>
        `;
    }
}

function renderTable(items) {
    const tbody = document.getElementById('history-body');
    tbody.innerHTML = '';

    if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem;">No scans found</td></tr>`;
        return;
    }

    items.forEach(item => {
        const row = document.createElement('tr');

        // Status Badge Logic
        let statusClass = 'badge badge-completed';
        let statusIcon = 'check';
        if (item.status === 'running') { statusClass = 'badge badge-running'; statusIcon = 'spinner fa-spin'; }
        if (item.status === 'failed') { statusClass = 'badge badge-failed'; statusIcon = 'xmark'; }

        // Risk Score Color
        let riskColor = 'var(--success)';
        if (item.risk_score >= 8) riskColor = 'var(--danger)';
        else if (item.risk_score >= 6) riskColor = '#f97316'; // orange
        else if (item.risk_score >= 4) riskColor = 'var(--warning)';

        row.innerHTML = `
            <td>
                <div style="font-weight: 500;">${item.target}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">${item.scan_id.substring(0, 8)}...</div>
            </td>
            <td>
                <span class="${statusClass}">
                    <i class="fa-solid fa-${statusIcon}" style="margin-right: 4px;"></i>
                    ${item.status}
                </span>
            </td>
            <td>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="risk-score" style="background-color: ${riskColor}; width: 28px; height: 28px; font-size: 0.75rem;">
                        ${item.risk_score.toFixed(1)}
                    </span>
                </div>
            </td>
            <td>${item.duration ? item.duration.toFixed(1) + 's' : '-'}</td>
            <td>${new Date(item.created_at).toLocaleString()}</td>
            <td>
                <div style="display: flex; gap: 0.5rem;">
                    <a href="/scan/${item.scan_id}" class="btn btn-sm btn-outline" title="View Details">
                        <i class="fa-solid fa-eye"></i>
                    </a>
                    <button class="btn btn-sm btn-danger" onclick="deleteScan('${item.scan_id}')" title="Delete">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderPagination(total, current) {
    const totalPages = Math.ceil(total / ITEMS_PER_PAGE);
    const container = document.getElementById('pagination-controls');
    container.innerHTML = '';

    if (totalPages <= 1) return;

    // Previous
    const prevBtn = document.createElement('button');
    prevBtn.className = 'btn btn-outline btn-sm';
    prevBtn.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
    prevBtn.disabled = current === 1;
    prevBtn.onclick = () => loadHistory(current - 1);
    container.appendChild(prevBtn);

    // Page Info
    const info = document.createElement('span');
    info.style.padding = '0.5rem';
    info.style.fontSize = '0.875rem';
    info.style.color = 'var(--text-secondary)';
    info.innerText = `Page ${current} of ${totalPages}`;
    container.appendChild(info);

    // Next
    const nextBtn = document.createElement('button');
    nextBtn.className = 'btn btn-outline btn-sm';
    nextBtn.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
    nextBtn.disabled = current === totalPages;
    nextBtn.onclick = () => loadHistory(current + 1);
    container.appendChild(nextBtn);
}

async function deleteScan(id) {
    if (!confirm('Are you sure you want to delete this scan?')) return;

    try {
        const res = await fetch(`/api/scan/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadHistory(currentPage); // Reload current page
        } else {
            alert('Failed to delete scan');
        }
    } catch (e) {
        console.error(e);
        alert('Error deleting scan');
    }
}
