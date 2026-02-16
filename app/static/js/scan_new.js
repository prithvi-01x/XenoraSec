// scan_new.js - New Scan Page Logic

document.addEventListener('DOMContentLoaded', () => {
    initScanForm();
    loadQueueStatus();
    setupAdvancedToggle();
    setupScanModeHandlers();
    setupTooltips();
});

// ==================== FORM INITIALIZATION ====================

function initScanForm() {
    const form = document.getElementById('scan-form');
    form.addEventListener('submit', handleScanSubmit);
}

async function handleScanSubmit(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const originalText = submitBtn.innerHTML;

    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Starting Scan...';

    try {
        // Gather form data
        const formData = gatherFormData();

        // Validate
        if (!validateFormData(formData)) {
            throw new Error('Invalid form data');
        }

        // Submit scan
        const response = await fetch('/api/scan/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start scan');
        }

        const result = await response.json();

        // Show success message
        showNotification('Scan started successfully!', 'success');

        // Redirect to progress page
        setTimeout(() => {
            window.location.href = `/scans/progress/${result.scan_id}`;
        }, 500);

    } catch (error) {
        console.error('Scan submission error:', error);
        showNotification(error.message, 'error');

        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// ==================== FORM DATA HANDLING ====================

function gatherFormData() {
    const target = document.getElementById('target').value.trim();
    const scanMode = document.querySelector('input[name="scan_mode"]:checked').value;

    // Base payload
    const payload = {
        target: target,
        scan_mode: scanMode
    };

    // Add advanced options if custom mode or advanced panel is open
    if (scanMode === 'custom' || document.getElementById('advanced-panel').classList.contains('open')) {
        payload.options = {
            port_range: document.getElementById('port_range').value,
            nmap_timing: document.getElementById('nmap_timing').value,
            nuclei_templates: getSelectedTemplates(),
            concurrency: parseInt(document.getElementById('concurrency').value),
            timeout_minutes: parseInt(document.getElementById('timeout').value),
            rate_limit: parseInt(document.getElementById('rate_limit').value),
            allow_private: document.getElementById('allow_private').checked,
            allow_localhost: document.getElementById('allow_localhost').checked
        };
    }

    return payload;
}

function getSelectedTemplates() {
    const checkboxes = document.querySelectorAll('input[name="templates"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function validateFormData(data) {
    // Validate target
    if (!data.target || data.target.length < 3) {
        showNotification('Please enter a valid target', 'error');
        return false;
    }

    // Validate options if present
    if (data.options) {
        if (data.options.concurrency < 1 || data.options.concurrency > 50) {
            showNotification('Concurrency must be between 1 and 50', 'error');
            return false;
        }

        if (data.options.timeout_minutes < 5 || data.options.timeout_minutes > 120) {
            showNotification('Timeout must be between 5 and 120 minutes', 'error');
            return false;
        }

        if (data.options.nuclei_templates.length === 0) {
            showNotification('Please select at least one template category', 'error');
            return false;
        }
    }

    return true;
}

// ==================== SCAN MODE HANDLING ====================

function setupScanModeHandlers() {
    const modeRadios = document.querySelectorAll('input[name="scan_mode"]');

    modeRadios.forEach(radio => {
        radio.addEventListener('change', handleScanModeChange);
    });
}

function handleScanModeChange(e) {
    const mode = e.target.value;
    const advancedPanel = document.getElementById('advanced-panel');
    const advancedToggle = document.getElementById('advanced-toggle');

    // Auto-configure based on mode
    switch (mode) {
        case 'quick':
            setQuickScanDefaults();
            // Collapse advanced panel for quick scan
            advancedPanel.classList.remove('open');
            advancedToggle.querySelector('i').classList.remove('fa-chevron-down');
            advancedToggle.querySelector('i').classList.add('fa-chevron-right');
            break;

        case 'deep':
            setDeepScanDefaults();
            // Collapse advanced panel for deep scan
            advancedPanel.classList.remove('open');
            advancedToggle.querySelector('i').classList.remove('fa-chevron-down');
            advancedToggle.querySelector('i').classList.add('fa-chevron-right');
            break;

        case 'custom':
            // Expand advanced panel for custom
            advancedPanel.classList.add('open');
            advancedToggle.querySelector('i').classList.remove('fa-chevron-right');
            advancedToggle.querySelector('i').classList.add('fa-chevron-down');
            break;
    }
}

function setQuickScanDefaults() {
    document.getElementById('port_range').value = '1-1000';
    document.getElementById('nmap_timing').value = 'T4';
    document.getElementById('timeout').value = '15';
    document.getElementById('concurrency').value = '10';

    // Select only medium+ severity templates
    document.querySelectorAll('input[name="templates"]').forEach(cb => {
        cb.checked = ['cve', 'misconfig', 'exposure'].includes(cb.value);
    });
}

function setDeepScanDefaults() {
    document.getElementById('port_range').value = '1-65535';
    document.getElementById('nmap_timing').value = 'T4';
    document.getElementById('timeout').value = '60';
    document.getElementById('concurrency').value = '10';

    // Select all templates
    document.querySelectorAll('input[name="templates"]').forEach(cb => {
        cb.checked = true;
    });
}

// ==================== ADVANCED OPTIONS TOGGLE ====================

function setupAdvancedToggle() {
    const toggle = document.getElementById('advanced-toggle');
    const panel = document.getElementById('advanced-panel');

    toggle.addEventListener('click', () => {
        const isOpen = panel.classList.toggle('open');
        const icon = toggle.querySelector('i');

        if (isOpen) {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
        } else {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
        }
    });
}

// ==================== QUEUE STATUS ====================

async function loadQueueStatus() {
    try {
        const response = await fetch('/api/scan/queue');
        const data = await response.json();

        document.getElementById('queue-running').textContent = data.running_scans || 0;
        document.getElementById('queue-available').textContent = data.available_slots || 0;

        // Update color based on availability
        const availableEl = document.getElementById('queue-available');
        if (data.available_slots === 0) {
            availableEl.style.color = 'var(--danger)';
        } else if (data.available_slots <= 2) {
            availableEl.style.color = 'var(--warning)';
        } else {
            availableEl.style.color = 'var(--success)';
        }

    } catch (error) {
        console.error('Failed to load queue status:', error);
        document.getElementById('queue-running').textContent = '?';
        document.getElementById('queue-available').textContent = '?';
    }

    // Refresh every 10 seconds
    setTimeout(loadQueueStatus, 10000);
}

// ==================== TOOLTIPS ====================

function setupTooltips() {
    const tooltipIcons = document.querySelectorAll('.tooltip-icon');

    tooltipIcons.forEach(icon => {
        const tooltip = icon.getAttribute('data-tooltip');

        icon.addEventListener('mouseenter', (e) => {
            showTooltip(e.target, tooltip);
        });

        icon.addEventListener('mouseleave', () => {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    // Remove existing tooltip
    hideTooltip();

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-popup';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

    setTimeout(() => tooltip.classList.add('visible'), 10);
}

function hideTooltip() {
    const existing = document.querySelector('.tooltip-popup');
    if (existing) {
        existing.remove();
    }
}

// ==================== NOTIFICATIONS ====================

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const icon = type === 'success' ? 'fa-check-circle' :
        type === 'error' ? 'fa-exclamation-circle' :
            'fa-info-circle';

    notification.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('visible'), 10);

    setTimeout(() => {
        notification.classList.remove('visible');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}
