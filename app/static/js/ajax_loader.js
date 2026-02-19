/**
 * AJAX Loader Utilities
 * Simulates slow network conditions for testing wait strategies
 */

/**
 * Wrapper for fetch with artificial delay
 * Use this instead of regular fetch to simulate slow responses
 */
window.slowFetch = function(url, options = {}) {
    const minDelay = options.minDelay || 500;
    const maxDelay = options.maxDelay || 2000;
    const delay = Math.random() * (maxDelay - minDelay) + minDelay;
    
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            fetch(url, options)
                .then(resolve)
                .catch(reject);
        }, delay);
    });
};

/**
 * Show inline loading spinner
 */
window.showInlineLoader = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const loader = document.createElement('div');
    loader.className = 'inline-loader text-center py-3';
    loader.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Ładowanie...</span>
        </div>
        <span class="ms-2 text-muted">Ładowanie danych...</span>
    `;
    
    container.innerHTML = '';
    container.appendChild(loader);
};

/**
 * Remove inline loading spinner
 */
window.hideInlineLoader = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const loader = container.querySelector('.inline-loader');
    if (loader) loader.remove();
};

/**
 * Simulate network latency for all fetch requests
 * This can be enabled/disabled via localStorage
 */
(function() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        // Check if slow mode is enabled
        const slowMode = localStorage.getItem('bugbank_slow_mode') === 'true';
        
        if (slowMode) {
            const delay = Math.random() * 2000 + 500; // 500-2500ms
            return new Promise(resolve => {
                setTimeout(() => {
                    resolve(originalFetch.apply(this, args));
                }, delay);
            });
        }
        
        return originalFetch.apply(this, args);
    };
})();

/**
 * Toggle slow mode (for testing)
 */
window.toggleSlowMode = function() {
    const current = localStorage.getItem('bugbank_slow_mode') === 'true';
    localStorage.setItem('bugbank_slow_mode', (!current).toString());
    console.log('Slow mode:', !current ? 'ENABLED' : 'DISABLED');
    return !current;
};

/**
 * Simulate stale element scenario
 * Refreshes an element after a delay, causing StaleElementReferenceException
 */
window.simulateStaleElement = function(elementId, delay = 2000) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    setTimeout(() => {
        const parent = element.parentNode;
        const clone = element.cloneNode(true);
        clone.id = elementId + '_refreshed_' + Date.now();
        parent.replaceChild(clone, element);
        console.log('Element refreshed (stale element scenario)');
    }, delay);
};

/**
 * Helper to wait for element to be present
 * Useful for debugging wait issues
 */
window.waitForElement = function(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const check = () => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
            } else if (Date.now() - startTime > timeout) {
                reject(new Error(`Element ${selector} not found after ${timeout}ms`));
            } else {
                requestAnimationFrame(check);
            }
        };
        
        check();
    });
};
