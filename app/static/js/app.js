/**
 * BugBank Main JavaScript
 * Contains global functionality and utilities
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
    
    // Cookie banner handling
    initCookieBanner();
    
    // Session timeout handling
    initSessionTimeout();
    
    // Load notifications
    loadNotifications();
    
    // Update sidebar message badge
    updateMessageBadge();
});

/**
 * Cookie Banner
 */
function initCookieBanner() {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('cookie-accept-btn');
    const settingsBtn = document.getElementById('cookie-settings-btn');
    
    if (!banner) return;
    
    // Check if already accepted
    if (!getCookie('cookies_accepted')) {
        banner.style.display = 'block';
    }
    
    if (acceptBtn) {
        acceptBtn.addEventListener('click', function() {
            setCookie('cookies_accepted', 'true', 365);
            banner.style.display = 'none';
        });
    }
    
    if (settingsBtn) {
        settingsBtn.addEventListener('click', function() {
            alert('Ustawienia plików cookies:\n\n✅ Niezbędne - zawsze włączone\n⬜ Analityczne - opcjonalne\n⬜ Marketingowe - opcjonalne');
        });
    }
}

/**
 * Session Timeout
 * Shows warning modal before session expires
 */
function initSessionTimeout() {
    let timeoutWarning;
    let timeoutLogout;
    let countdownInterval;
    
    const SESSION_WARNING_TIME = 4 * 60 * 1000; // 4 minutes
    const SESSION_TIMEOUT = 5 * 60 * 1000; // 5 minutes
    
    const modal = document.getElementById('session-timeout-modal');
    if (!modal) return;
    
    const bsModal = new bootstrap.Modal(modal);
    const countdownEl = document.getElementById('timeout-countdown');
    const extendBtn = document.getElementById('extend-session-btn');
    const logoutBtn = document.getElementById('logout-btn');
    
    function resetTimers() {
        clearTimeout(timeoutWarning);
        clearTimeout(timeoutLogout);
        clearInterval(countdownInterval);
        
        timeoutWarning = setTimeout(showWarning, SESSION_WARNING_TIME);
    }
    
    function showWarning() {
        let countdown = 60;
        countdownEl.textContent = countdown;
        bsModal.show();
        
        countdownInterval = setInterval(function() {
            countdown--;
            countdownEl.textContent = countdown;
            
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                window.location.href = '/logout';
            }
        }, 1000);
    }
    
    if (extendBtn) {
        extendBtn.addEventListener('click', function() {
            // Ping server to extend session
            fetch('/check-session')
                .then(response => {
                    if (response.ok) {
                        bsModal.hide();
                        clearInterval(countdownInterval);
                        resetTimers();
                    }
                });
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.location.href = '/logout';
        });
    }
    
    // Reset on user activity
    ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
        document.addEventListener(event, resetTimers, {passive: true});
    });
    
    // Initial timer
    resetTimers();
}

/**
 * Load notifications for navbar
 */
function loadNotifications() {
    const badge = document.getElementById('notification-badge');
    const countEl = document.getElementById('notification-count');
    const listEl = document.getElementById('notifications-list');
    
    if (!badge) return;
    
    fetch('/api/dashboard/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.unread_count > 0) {
                badge.style.display = 'inline-block';
                countEl.textContent = data.unread_count;
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(() => {
            badge.style.display = 'none';
        });
}

/**
 * Update sidebar message badge
 */
function updateMessageBadge() {
    const badge = document.getElementById('sidebar-message-badge');
    if (!badge) return;
    
    fetch('/api/messages/unread-count')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                badge.style.display = 'inline-block';
                badge.textContent = data.count;
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(() => {
            badge.style.display = 'none';
        });
}

/**
 * Cookie utilities
 */
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i].trim();
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'PLN') {
    return new Intl.NumberFormat('pl-PL', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

/**
 * Debounce function
 */
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
