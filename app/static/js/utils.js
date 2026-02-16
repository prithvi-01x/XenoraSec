/**
 * Global Utilities
 * Shared functions used across the application
 */

(function () {
    'use strict';

    // ==================== NOTIFICATION SYSTEM ====================

    /**
     * Show notification toast
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info, warning)
     * @param {number} duration - Duration in milliseconds (default: 5000)
     */
    window.showNotification = function (message, type = 'info', duration = 5000) {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icon = type === 'success' ? 'fa-check-circle' :
            type === 'error' ? 'fa-exclamation-circle' :
                type === 'warning' ? 'fa-exclamation-triangle' :
                    'fa-info-circle';

        notification.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fa-solid fa-times"></i>
            </button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('visible'), 10);

        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    };

    // ==================== API HELPERS ====================

    /**
     * Make API request with error handling
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise}
     */
    window.apiRequest = async function (url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    };

    // ==================== DATE/TIME FORMATTING ====================

    /**
     * Format date to locale string
     * @param {string|Date} date - Date to format
     * @returns {string}
     */
    window.formatDate = function (date) {
        const d = new Date(date);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
    };

    /**
     * Get relative time string (e.g., "2 hours ago")
     * @param {string|Date} date - Date to format
     * @returns {string}
     */
    window.getRelativeTime = function (date) {
        const now = new Date();
        const then = new Date(date);
        const diffMs = now - then;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) return 'just now';
        if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
        if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
        if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;

        return formatDate(date);
    };

    // ==================== DOM HELPERS ====================

    /**
     * Create element from HTML string
     * @param {string} html - HTML string
     * @returns {Element}
     */
    window.createElementFromHTML = function (html) {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    };

    /**
     * Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function}
     */
    window.debounce = function (func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    /**
     * Throttle function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Limit in milliseconds
     * @returns {Function}
     */
    window.throttle = function (func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };

    // ==================== VALIDATION HELPERS ====================

    /**
     * Validate email
     * @param {string} email - Email to validate
     * @returns {boolean}
     */
    window.isValidEmail = function (email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    };

    /**
     * Validate URL
     * @param {string} url - URL to validate
     * @returns {boolean}
     */
    window.isValidUrl = function (url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    };

    /**
     * Validate IP address
     * @param {string} ip - IP to validate
     * @returns {boolean}
     */
    window.isValidIP = function (ip) {
        const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/;
        const ipv6 = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
        return ipv4.test(ip) || ipv6.test(ip);
    };

    // ==================== STORAGE HELPERS ====================

    /**
     * Local storage wrapper with JSON support
     */
    window.storage = {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                console.error('Storage set error:', error);
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.error('Storage remove error:', error);
            }
        },

        clear() {
            try {
                localStorage.clear();
            } catch (error) {
                console.error('Storage clear error:', error);
            }
        }
    };

    // ==================== RISK SCORE HELPERS ====================

    /**
     * Get risk color based on score
     * @param {number} score - Risk score (0-10)
     * @returns {string} - Color hex code
     */
    window.getRiskColor = function (score) {
        if (score >= 8) return '#ef4444'; // Critical - Red
        if (score >= 6) return '#f97316'; // High - Orange
        if (score >= 4) return '#eab308'; // Medium - Yellow
        return '#22c55e'; // Low - Green
    };

    /**
     * Get risk label based on score
     * @param {number} score - Risk score (0-10)
     * @returns {string} - Risk label
     */
    window.getRiskLabel = function (score) {
        if (score >= 8) return 'Critical';
        if (score >= 6) return 'High';
        if (score >= 4) return 'Medium';
        return 'Low';
    };

    // ==================== LOADING STATES ====================

    /**
     * Show skeleton loader
     * @param {string} selector - Container selector
     */
    window.showSkeleton = function (selector) {
        const container = document.querySelector(selector);
        if (!container) return;

        container.innerHTML = `
            <div class="skeleton-loader">
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
            </div>
        `;
    };

    /**
     * Create loading spinner element
     * @returns {HTMLElement}
     */
    window.createSpinner = function () {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        return spinner;
    };

    // ==================== CLIPBOARD ====================

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>}
     */
    window.copyToClipboard = async function (text) {
        try {
            await navigator.clipboard.writeText(text);
            showNotification('Copied to clipboard', 'success', 2000);
            return true;
        } catch (error) {
            console.error('Clipboard error:', error);
            showNotification('Failed to copy', 'error', 2000);
            return false;
        }
    };

    // ==================== CONFIRMATION DIALOG ====================

    /**
     * Show confirmation dialog
     * @param {string} message - Confirmation message
     * @param {string} confirmText - Confirm button text
     * @param {string} cancelText - Cancel button text
     * @returns {Promise<boolean>}
     */
    window.confirmDialog = function (message, confirmText = 'Confirm', cancelText = 'Cancel') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <h3>Confirm Action</h3>
                        <p>${message}</p>
                        <div class="modal-actions">
                            <button class="btn btn-outline" data-action="cancel">${cancelText}</button>
                            <button class="btn btn-danger" data-action="confirm">${confirmText}</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            modal.addEventListener('click', (e) => {
                if (e.target.dataset.action === 'confirm') {
                    resolve(true);
                    modal.remove();
                } else if (e.target.dataset.action === 'cancel' || e.target === modal) {
                    resolve(false);
                    modal.remove();
                }
            });

            setTimeout(() => modal.classList.add('visible'), 10);
        });
    };

    // ==================== EXPORT ====================

    console.log('✅ Global utilities loaded');

})();
