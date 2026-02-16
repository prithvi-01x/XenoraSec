/**
 * SPA Router - Vanilla JavaScript Single Page Application Router
 * Handles client-side navigation without full page reloads
 */

(function () {
    'use strict';

    const SPARouter = {
        // Configuration
        config: {
            contentContainer: '#main-container',
            loadingIndicator: '#page-loader',
            transitionDuration: 300,
            scrollRestoration: true
        },

        // State management
        state: {
            currentPage: null,
            scrollPositions: new Map(),
            pageScripts: new Map(),
            isNavigating: false
        },

        /**
         * Initialize the SPA router
         */
        init() {
            console.log('🚀 Initializing SPA Router...');

            // Intercept all navigation clicks
            this.interceptNavigationClicks();

            // Handle browser back/forward buttons
            this.handleBrowserNavigation();

            // Store initial page state
            this.state.currentPage = window.location.pathname;

            // Replace initial history state
            history.replaceState(
                { path: this.state.currentPage, timestamp: Date.now() },
                '',
                this.state.currentPage
            );

            console.log('✅ SPA Router initialized');
        },

        /**
         * Intercept all navigation link clicks
         */
        interceptNavigationClicks() {
            document.addEventListener('click', (e) => {
                // Find the closest anchor tag
                const link = e.target.closest('a');

                if (!link) return;

                // Get the href
                const href = link.getAttribute('href');

                // Ignore external links, hash links, and special attributes
                if (!href ||
                    href.startsWith('http') ||
                    href.startsWith('#') ||
                    link.hasAttribute('data-no-spa') ||
                    link.target === '_blank') {
                    return;
                }

                // Prevent default navigation
                e.preventDefault();

                // Navigate using SPA router
                this.navigateTo(href);
            });
        },

        /**
         * Handle browser back/forward navigation
         */
        handleBrowserNavigation() {
            window.addEventListener('popstate', (e) => {
                if (e.state && e.state.path) {
                    // Navigate without pushing to history
                    this.navigateTo(e.state.path, false);
                }
            });
        },

        /**
         * Navigate to a new page
         * @param {string} url - The URL to navigate to
         * @param {boolean} pushState - Whether to push to browser history
         */
        async navigateTo(url, pushState = true) {
            // Prevent concurrent navigation
            if (this.state.isNavigating) {
                console.warn('Navigation already in progress');
                return;
            }

            this.state.isNavigating = true;

            try {
                // Save current scroll position
                if (this.config.scrollRestoration && this.state.currentPage) {
                    this.state.scrollPositions.set(
                        this.state.currentPage,
                        window.scrollY
                    );
                }

                // Update active navigation link
                this.updateActiveNavLink(url);

                // Show loading indicator
                this.showLoader();

                // Fetch new content
                const html = await this.fetchPageContent(url);

                // Hide current content with fade out
                await this.fadeOut();

                // Clean up current page scripts
                this.cleanupPageScripts();

                // Update content
                this.updateContent(html);

                // Initialize new page scripts
                await this.initializePageScripts(url);

                // Fade in new content
                await this.fadeIn();

                // Restore or reset scroll position
                this.handleScrollRestoration(url);

                // Update browser history
                if (pushState) {
                    history.pushState(
                        { path: url, timestamp: Date.now() },
                        '',
                        url
                    );
                }

                // Update current page
                this.state.currentPage = url;

                // Update page title
                this.updatePageTitle(url);

                // Hide loading indicator
                this.hideLoader();

                // Trigger custom event
                this.dispatchNavigationEvent(url);

            } catch (error) {
                console.error('Navigation error:', error);
                this.showError('Failed to load page. Please try again.');

                // Fallback to full page load
                window.location.href = url;
            } finally {
                this.state.isNavigating = false;
            }
        },

        /**
         * Fetch page content from server
         * @param {string} url - The URL to fetch
         * @returns {Promise<string>} - The HTML content
         */
        async fetchPageContent(url) {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.text();
        },

        /**
         * Update the content container
         * @param {string} html - The HTML content to insert
         */
        updateContent(html) {
            const container = document.querySelector(this.config.contentContainer);

            if (!container) {
                console.error('Content container not found');
                return;
            }

            // Extract just the content (remove full HTML structure if present)
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            // Try to find the main container in the fetched HTML
            const fetchedContainer = tempDiv.querySelector('.container') || tempDiv;

            container.innerHTML = fetchedContainer.innerHTML;
        },

        /**
         * Update active navigation link
         * @param {string} url - The current URL
         */
        updateActiveNavLink(url) {
            // Remove all active classes
            document.querySelectorAll('.nav-item.active').forEach(item => {
                item.classList.remove('active');
            });

            // Add active class to matching link
            const matchingLink = document.querySelector(`.nav-item[href="${url}"]`);
            if (matchingLink) {
                matchingLink.classList.add('active');
            }

            // Handle partial matches (e.g., /scans/history matches /scans/*)
            if (!matchingLink) {
                const partialMatch = Array.from(document.querySelectorAll('.nav-item'))
                    .find(link => {
                        const href = link.getAttribute('href');
                        return href && url.startsWith(href) && href !== '/';
                    });

                if (partialMatch) {
                    partialMatch.classList.add('active');
                }
            }
        },

        /**
         * Initialize page-specific scripts
         * @param {string} url - The current URL
         */
        async initializePageScripts(url) {
            // Map URLs to their script files
            const scriptMap = {
                '/dashboard': '/static/js/dashboard.js',
                '/scans/new': '/static/js/scan_new.js',
                '/scans/history': '/static/js/history.js',
                '/scan/': '/static/js/scan_detail.js',
                '/scans/progress/': '/static/js/scan_progress.js'
            };

            // Find matching script
            let scriptUrl = null;
            for (const [pattern, script] of Object.entries(scriptMap)) {
                if (url.startsWith(pattern)) {
                    scriptUrl = script;
                    break;
                }
            }

            if (!scriptUrl) return;

            // Load and execute script
            try {
                // Check if script is already loaded
                if (this.state.pageScripts.has(scriptUrl)) {
                    // Re-initialize if script has init function
                    const initFn = this.state.pageScripts.get(scriptUrl);
                    if (typeof initFn === 'function') {
                        initFn();
                    }
                    return;
                }

                // Load script dynamically
                await this.loadScript(scriptUrl);

                // Trigger DOMContentLoaded for the new content
                this.triggerContentLoaded();

            } catch (error) {
                console.error('Failed to load page script:', error);
            }
        },

        /**
         * Load a script dynamically
         * @param {string} url - Script URL
         * @returns {Promise}
         */
        loadScript(url) {
            return new Promise((resolve, reject) => {
                // Check if script already exists
                const existing = document.querySelector(`script[src="${url}"]`);
                if (existing) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = url;
                script.async = true;
                script.onload = () => resolve();
                script.onerror = () => reject(new Error(`Failed to load script: ${url}`));

                document.body.appendChild(script);
            });
        },

        /**
         * Trigger DOMContentLoaded event for dynamically loaded content
         */
        triggerContentLoaded() {
            const event = new Event('DOMContentLoaded', {
                bubbles: true,
                cancelable: true
            });
            document.dispatchEvent(event);
        },

        /**
         * Clean up current page scripts
         */
        cleanupPageScripts() {
            // Clear any intervals or timeouts
            // This is a placeholder - specific cleanup should be handled by page scripts
            const event = new CustomEvent('page:cleanup');
            document.dispatchEvent(event);
        },

        /**
         * Handle scroll restoration
         * @param {string} url - The current URL
         */
        handleScrollRestoration(url) {
            if (this.config.scrollRestoration && this.state.scrollPositions.has(url)) {
                // Restore previous scroll position
                const scrollY = this.state.scrollPositions.get(url);
                window.scrollTo(0, scrollY);
            } else {
                // Scroll to top for new pages
                window.scrollTo(0, 0);
            }
        },

        /**
         * Update page title based on URL
         * @param {string} url - The current URL
         */
        updatePageTitle(url) {
            const titleMap = {
                '/dashboard': 'Dashboard',
                '/scans/new': 'New Scan',
                '/scans/history': 'Scan History',
                '/scans/progress/': 'Scan Progress',
                '/scan/': 'Scan Details',
                '/settings': 'Settings'
            };

            let title = 'VulnScanner';
            for (const [pattern, pageTitle] of Object.entries(titleMap)) {
                if (url.startsWith(pattern)) {
                    title = `${pageTitle} | VulnScanner`;
                    break;
                }
            }

            document.title = title;
        },

        /**
         * Fade out animation
         * @returns {Promise}
         */
        fadeOut() {
            return new Promise(resolve => {
                const container = document.querySelector(this.config.contentContainer);
                container.style.opacity = '0';
                container.style.transform = 'translateY(10px)';

                setTimeout(resolve, this.config.transitionDuration);
            });
        },

        /**
         * Fade in animation
         * @returns {Promise}
         */
        fadeIn() {
            return new Promise(resolve => {
                const container = document.querySelector(this.config.contentContainer);

                // Reset transform
                container.style.transform = 'translateY(0)';

                // Trigger reflow
                container.offsetHeight;

                // Fade in
                container.style.opacity = '1';

                setTimeout(resolve, this.config.transitionDuration);
            });
        },

        /**
         * Show loading indicator
         */
        showLoader() {
            const loader = document.querySelector(this.config.loadingIndicator);
            if (loader) {
                loader.style.display = 'flex';
            }
        },

        /**
         * Hide loading indicator
         */
        hideLoader() {
            const loader = document.querySelector(this.config.loadingIndicator);
            if (loader) {
                loader.style.display = 'none';
            }
        },

        /**
         * Show error message
         * @param {string} message - Error message
         */
        showError(message) {
            if (window.showNotification) {
                window.showNotification(message, 'error');
            } else {
                alert(message);
            }
        },

        /**
         * Dispatch navigation event
         * @param {string} url - The navigated URL
         */
        dispatchNavigationEvent(url) {
            const event = new CustomEvent('spa:navigated', {
                detail: { url, timestamp: Date.now() }
            });
            document.dispatchEvent(event);
        }
    };

    // Expose to global scope
    window.SPARouter = SPARouter;

})();
