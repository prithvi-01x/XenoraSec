/**
 * Persistent Scan Queue Widget
 * Shows active scans across all pages
 */

(function () {
    'use strict';

    const ScanQueueWidget = {
        config: {
            updateInterval: 5000, // 5 seconds
            maxVisibleScans: 5
        },

        state: {
            isExpanded: true,
            updateTimer: null,
            activeScans: []
        },

        /**
         * Initialize the widget
         */
        init() {
            console.log('🔄 Initializing Scan Queue Widget...');

            this.setupEventListeners();
            this.loadActiveScans();
            this.startAutoUpdate();

            console.log('✅ Scan Queue Widget initialized');
        },

        /**
         * Setup event listeners
         */
        setupEventListeners() {
            const toggleBtn = document.getElementById('toggle-queue');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => this.toggle());
            }

            // Listen for new scan events
            document.addEventListener('scan:started', (e) => {
                this.addScan(e.detail);
            });

            // Listen for scan completion
            document.addEventListener('scan:completed', (e) => {
                this.removeScan(e.detail.scan_id);
            });

            // Cleanup on page unload
            window.addEventListener('beforeunload', () => {
                this.stopAutoUpdate();
            });
        },

        /**
         * Load active scans from API
         */
        async loadActiveScans() {
            try {
                const response = await fetch('/api/scan/queue');
                const data = await response.json();

                // Fetch details of running scans
                if (data.running_scans > 0) {
                    await this.fetchRunningScanDetails();
                } else {
                    this.updateUI([]);
                }

            } catch (error) {
                console.error('Failed to load active scans:', error);
            }
        },

        /**
         * Fetch running scan details
         */
        async fetchRunningScanDetails() {
            try {
                const response = await fetch('/api/scan/history?status=running&limit=10');
                const data = await response.json();

                this.state.activeScans = data.items || [];
                this.updateUI(this.state.activeScans);

            } catch (error) {
                console.error('Failed to fetch scan details:', error);
            }
        },

        /**
         * Update widget UI
         * @param {Array} scans - Array of active scans
         */
        updateUI(scans) {
            const queueBody = document.getElementById('queue-body');
            if (!queueBody) return;

            if (scans.length === 0) {
                queueBody.innerHTML = '<div class="queue-empty">No active scans</div>';
                return;
            }

            const html = scans.slice(0, this.config.maxVisibleScans).map(scan => `
                <div class="queue-item" data-scan-id="${scan.scan_id}">
                    <div class="queue-item-header">
                        <span class="queue-target">${this.truncate(scan.target, 25)}</span>
                        <span class="queue-status">
                            <i class="fa-solid fa-spinner fa-spin"></i>
                        </span>
                    </div>
                    <div class="queue-item-meta">
                        <span class="queue-time">${this.getElapsedTime(scan.created_at)}</span>
                        <a href="/scans/progress/${scan.scan_id}" class="queue-view">
                            View
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            `).join('');

            queueBody.innerHTML = html;

            // Update widget badge
            this.updateBadge(scans.length);
        },

        /**
         * Add a new scan to the widget
         * @param {Object} scan - Scan object
         */
        addScan(scan) {
            // Check if scan already exists
            const exists = this.state.activeScans.some(s => s.scan_id === scan.scan_id);
            if (exists) return;

            this.state.activeScans.unshift(scan);
            this.updateUI(this.state.activeScans);

            // Show notification
            if (window.showNotification) {
                window.showNotification(`Scan started: ${scan.target}`, 'success');
            }
        },

        /**
         * Remove a scan from the widget
         * @param {string} scanId - Scan ID
         */
        removeScan(scanId) {
            this.state.activeScans = this.state.activeScans.filter(s => s.scan_id !== scanId);
            this.updateUI(this.state.activeScans);
        },

        /**
         * Toggle widget visibility
         */
        toggle() {
            const queueBody = document.getElementById('queue-body');
            const toggleBtn = document.getElementById('toggle-queue');

            if (!queueBody || !toggleBtn) return;

            this.state.isExpanded = !this.state.isExpanded;

            if (this.state.isExpanded) {
                queueBody.style.display = 'block';
                toggleBtn.querySelector('i').classList.remove('fa-chevron-up');
                toggleBtn.querySelector('i').classList.add('fa-chevron-down');
            } else {
                queueBody.style.display = 'none';
                toggleBtn.querySelector('i').classList.remove('fa-chevron-down');
                toggleBtn.querySelector('i').classList.add('fa-chevron-up');
            }
        },

        /**
         * Update badge count
         * @param {number} count - Number of active scans
         */
        updateBadge(count) {
            const widget = document.getElementById('scan-queue-widget');
            if (!widget) return;

            let badge = widget.querySelector('.queue-badge');

            if (count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'queue-badge';
                    widget.querySelector('.queue-header h4').appendChild(badge);
                }
                badge.textContent = count;
            } else if (badge) {
                badge.remove();
            }
        },

        /**
         * Start auto-update timer
         */
        startAutoUpdate() {
            this.state.updateTimer = setInterval(() => {
                this.loadActiveScans();
            }, this.config.updateInterval);
        },

        /**
         * Stop auto-update timer
         */
        stopAutoUpdate() {
            if (this.state.updateTimer) {
                clearInterval(this.state.updateTimer);
                this.state.updateTimer = null;
            }
        },

        /**
         * Get elapsed time string
         * @param {string} timestamp - ISO timestamp
         * @returns {string}
         */
        getElapsedTime(timestamp) {
            const start = new Date(timestamp);
            const now = new Date();
            const diff = Math.floor((now - start) / 1000); // seconds

            if (diff < 60) return `${diff}s`;
            if (diff < 3600) return `${Math.floor(diff / 60)}m`;
            return `${Math.floor(diff / 3600)}h`;
        },

        /**
         * Truncate string
         * @param {string} str - String to truncate
         * @param {number} maxLength - Maximum length
         * @returns {string}
         */
        truncate(str, maxLength) {
            if (str.length <= maxLength) return str;
            return str.substring(0, maxLength - 3) + '...';
        }
    };

    // Expose to global scope
    window.ScanQueueWidget = ScanQueueWidget;

})();
