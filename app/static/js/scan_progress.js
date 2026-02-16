// scan_progress.js - Real-time Scan Progress Tracking

let scanId = window.SCAN_ID;
let autoScroll = true;
let startTime = Date.now();
let elapsedTimer = null;
let pollingInterval = null;
let currentPhase = 'validation';

document.addEventListener('DOMContentLoaded', () => {
    initProgressTracking();
    startElapsedTimer();
    setupEventListeners();
});

// ==================== INITIALIZATION ====================

function initProgressTracking() {
    // Try WebSocket first, fallback to polling
    if ('WebSocket' in window) {
        // WebSocket not implemented yet, use smart polling
        startSmartPolling();
    } else {
        startSmartPolling();
    }
}

// ==================== SMART POLLING ====================

function startSmartPolling() {
    updateConnectionStatus('polling', 'Polling for updates...');

    // Initial fetch
    fetchScanStatus();

    // Start polling with adaptive interval
    pollingInterval = setInterval(() => {
        fetchScanStatus();
    }, 2000); // Start with 2 second interval
}

async function fetchScanStatus() {
    try {
        const response = await fetch(`/api/scan/results/${scanId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch scan status');
        }

        const data = await response.json();

        // Update UI with scan data
        updateScanProgress(data);

        // Check if scan is complete
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'timeout') {
            stopPolling();
            handleScanCompletion(data);
        }

        updateConnectionStatus('connected', 'Live updates active');

    } catch (error) {
        console.error('Polling error:', error);
        updateConnectionStatus('error', 'Connection error');
        addLogEntry('error', 'Failed to fetch scan status');
    }
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// ==================== UI UPDATES ====================

function updateScanProgress(data) {
    // Update target name
    document.getElementById('target-name').textContent = data.target || 'Unknown Target';

    // Determine current phase and progress
    const phaseInfo = determinePhase(data);
    updatePhaseTracker(phaseInfo.phase, phaseInfo.progress);

    // Update statistics
    updateStatistics(data);

    // Add log entries based on data changes
    generateLogEntries(data);
}

function determinePhase(data) {
    const status = data.status;
    const nmapData = data.nmap || {};
    const nucleiData = data.nuclei || {};

    let phase = 'validation';
    let progress = 0;

    if (status === 'running') {
        // Check which phase we're in based on available data
        if (nucleiData.status === 'completed') {
            phase = 'ai';
            progress = 80;
        } else if (nucleiData.status === 'running' || nucleiData.total_vulnerabilities > 0) {
            phase = 'nuclei';
            progress = 60;
        } else if (nmapData.status === 'completed' || nmapData.total_ports > 0) {
            phase = 'nuclei';
            progress = 40;
        } else if (nmapData.status === 'running') {
            phase = 'nmap';
            progress = 20;
        } else {
            phase = 'validation';
            progress = 10;
        }
    } else if (status === 'completed') {
        phase = 'complete';
        progress = 100;
    } else if (status === 'failed' || status === 'timeout') {
        progress = 0;
    }

    return { phase, progress };
}

function updatePhaseTracker(phase, progress) {
    const phases = ['validation', 'nmap', 'nuclei', 'ai', 'complete'];
    const currentIndex = phases.indexOf(phase);

    phases.forEach((p, index) => {
        const phaseEl = document.querySelector(`.phase-item[data-phase="${p}"]`);
        const statusEl = phaseEl.querySelector('.phase-status');

        if (index < currentIndex) {
            // Completed phase
            phaseEl.classList.remove('active', 'pending');
            phaseEl.classList.add('completed');
            statusEl.textContent = 'Complete';
        } else if (index === currentIndex) {
            // Active phase
            phaseEl.classList.remove('completed', 'pending');
            phaseEl.classList.add('active');
            statusEl.textContent = 'Running...';
        } else {
            // Pending phase
            phaseEl.classList.remove('completed', 'active');
            phaseEl.classList.add('pending');
            statusEl.textContent = 'Pending';
        }
    });

    // Update progress bar
    updateProgressBar(progress);

    // Store current phase for log generation
    if (phase !== currentPhase) {
        currentPhase = phase;
        addLogEntry('info', `Phase: ${phase.toUpperCase()} started`);
    }
}

function updateProgressBar(progress) {
    const fillEl = document.getElementById('progress-bar-fill');
    const percentEl = document.getElementById('progress-percentage');

    fillEl.style.width = progress + '%';
    percentEl.textContent = progress + '%';
}

function updateStatistics(data) {
    // Open ports
    const openPorts = data.nmap?.total_ports || 0;
    document.getElementById('open-ports').textContent = openPorts;

    // Vulnerabilities
    const vulns = data.nuclei?.total_vulnerabilities || 0;
    document.getElementById('vulnerabilities-found').textContent = vulns;

    // Risk score
    const riskScore = data.risk_score || 0;
    const riskEl = document.getElementById('current-risk');
    if (riskScore > 0) {
        riskEl.textContent = riskScore.toFixed(1);
        riskEl.style.color = getRiskColor(riskScore);
    } else {
        riskEl.textContent = '-';
    }

    // Severity breakdown
    const severity = data.nuclei?.severity_distribution || {};
    document.getElementById('count-critical').textContent = severity.critical || 0;
    document.getElementById('count-high').textContent = severity.high || 0;
    document.getElementById('count-medium').textContent = severity.medium || 0;
    document.getElementById('count-low').textContent = severity.low || 0;
}

function getRiskColor(score) {
    if (score >= 8) return '#ef4444';
    if (score >= 6) return '#f97316';
    if (score >= 4) return '#eab308';
    return '#22c55e';
}

// ==================== LOG MANAGEMENT ====================

let lastLogState = {
    ports: 0,
    vulns: 0,
    phase: 'validation'
};

function generateLogEntries(data) {
    const nmapPorts = data.nmap?.total_ports || 0;
    const nucleiVulns = data.nuclei?.total_vulnerabilities || 0;

    // Log port discoveries
    if (nmapPorts > lastLogState.ports) {
        const newPorts = nmapPorts - lastLogState.ports;
        addLogEntry('success', `✓ Discovered ${newPorts} new open port(s). Total: ${nmapPorts}`);
        lastLogState.ports = nmapPorts;
    }

    // Log vulnerability discoveries
    if (nucleiVulns > lastLogState.vulns) {
        const newVulns = nucleiVulns - lastLogState.vulns;
        addLogEntry('warning', `⚠ Found ${newVulns} new vulnerability(ies). Total: ${nucleiVulns}`);
        lastLogState.vulns = nucleiVulns;
    }

    // Log specific high-severity findings
    if (data.nuclei?.vulnerabilities) {
        data.nuclei.vulnerabilities.forEach(vuln => {
            if (vuln.severity === 'critical' && !isVulnLogged(vuln.id)) {
                addLogEntry('error', `🔴 CRITICAL: ${vuln.name || vuln.template_id}`);
                markVulnLogged(vuln.id);
            }
        });
    }
}

const loggedVulns = new Set();

function isVulnLogged(vulnId) {
    return loggedVulns.has(vulnId);
}

function markVulnLogged(vulnId) {
    loggedVulns.add(vulnId);
}

function addLogEntry(type, message) {
    const logsViewer = document.getElementById('logs-viewer');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;

    const timestamp = new Date().toLocaleTimeString();

    logEntry.innerHTML = `
        <span class="log-time">[${timestamp}]</span>
        <span class="log-message">${message}</span>
    `;

    logsViewer.appendChild(logEntry);

    // Auto-scroll if enabled
    if (autoScroll) {
        logsViewer.scrollTop = logsViewer.scrollHeight;
    }

    // Limit log entries to 100
    const entries = logsViewer.querySelectorAll('.log-entry');
    if (entries.length > 100) {
        entries[0].remove();
    }
}

// ==================== SCAN COMPLETION ====================

function handleScanCompletion(data) {
    stopPolling();
    stopElapsedTimer();

    const completionSection = document.getElementById('completion-actions');
    const titleEl = document.getElementById('completion-title');
    const descEl = document.getElementById('completion-description');
    const viewBtn = document.getElementById('view-report-btn');

    if (data.status === 'completed') {
        titleEl.textContent = '✓ Scan Complete!';
        descEl.textContent = `Found ${data.nuclei?.total_vulnerabilities || 0} vulnerabilities with a risk score of ${data.risk_score?.toFixed(1) || 0}`;
        viewBtn.onclick = () => window.location.href = `/scan/${scanId}`;

        addLogEntry('success', '✓ Scan completed successfully');
        updateConnectionStatus('completed', 'Scan finished');

    } else if (data.status === 'failed') {
        titleEl.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Scan Failed';
        descEl.textContent = data.error || 'The scan encountered an error and could not complete.';
        viewBtn.textContent = 'View Details';
        viewBtn.onclick = () => window.location.href = `/scan/${scanId}`;

        addLogEntry('error', `✗ Scan failed: ${data.error || 'Unknown error'}`);
        updateConnectionStatus('error', 'Scan failed');

    } else if (data.status === 'timeout') {
        titleEl.innerHTML = '<i class="fa-solid fa-clock"></i> Scan Timeout';
        descEl.textContent = 'The scan exceeded the maximum allowed time.';
        viewBtn.textContent = 'View Partial Results';
        viewBtn.onclick = () => window.location.href = `/scan/${scanId}`;

        addLogEntry('warning', '⏱ Scan timed out');
        updateConnectionStatus('timeout', 'Scan timeout');
    }

    completionSection.style.display = 'flex';
}

// ==================== ELAPSED TIME ====================

function startElapsedTimer() {
    updateElapsedTime();
    elapsedTimer = setInterval(updateElapsedTime, 1000);
}

function stopElapsedTimer() {
    if (elapsedTimer) {
        clearInterval(elapsedTimer);
        elapsedTimer = null;
    }
}

function updateElapsedTime() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    document.getElementById('elapsed-time').textContent =
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// ==================== CONNECTION STATUS ====================

function updateConnectionStatus(status, text) {
    const indicator = document.getElementById('connection-indicator');
    const dot = indicator.querySelector('.status-dot');
    const textEl = indicator.querySelector('.status-text');

    // Remove all status classes
    dot.classList.remove('status-connected', 'status-polling', 'status-error', 'status-completed', 'status-timeout');

    // Add appropriate class
    dot.classList.add(`status-${status}`);
    textEl.textContent = text;
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Auto-scroll toggle
    document.getElementById('auto-scroll-toggle').addEventListener('click', () => {
        autoScroll = !autoScroll;
        const icon = document.querySelector('#auto-scroll-toggle i');

        if (autoScroll) {
            icon.style.color = 'var(--primary)';
            const logsViewer = document.getElementById('logs-viewer');
            logsViewer.scrollTop = logsViewer.scrollHeight;
        } else {
            icon.style.color = 'var(--text-secondary)';
        }
    });

    // Clear logs
    document.getElementById('clear-logs').addEventListener('click', () => {
        const logsViewer = document.getElementById('logs-viewer');
        logsViewer.innerHTML = '<div class="log-entry log-info"><span class="log-time">[--:--:--]</span><span class="log-message">Logs cleared</span></div>';
    });
}

// ==================== CLEANUP ====================

window.addEventListener('beforeunload', () => {
    stopPolling();
    stopElapsedTimer();
});
