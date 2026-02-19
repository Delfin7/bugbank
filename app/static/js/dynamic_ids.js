/**
 * Dynamic IDs Generator
 * This script regenerates element IDs on page load to simulate dynamic content
 * This is a challenge for Selenium testers - they need to use other locators!
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements that should have dynamic IDs (marked with data-dynamic-id)
    const dynamicElements = document.querySelectorAll('[data-dynamic-id]');
    
    dynamicElements.forEach(el => {
        const baseId = el.dataset.dynamicId;
        const randomSuffix = generateRandomString(6);
        el.id = `${baseId}_${randomSuffix}`;
    });
    
    // Also randomize some existing IDs (simulating real-world dynamic content)
    randomizeExistingIds();
});

/**
 * Generate random alphanumeric string
 */
function generateRandomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Randomize some existing element IDs
 * This simulates frameworks that generate dynamic IDs
 */
function randomizeExistingIds() {
    // Find elements with IDs that start with certain prefixes
    const prefixes = ['btn_', 'el_', 'nav_', 'action-btn-'];
    
    prefixes.forEach(prefix => {
        document.querySelectorAll(`[id^="${prefix}"]`).forEach(el => {
            // Only randomize if not already randomized (check for underscore pattern)
            if (!el.id.match(/_[a-z0-9]{6}$/)) {
                const newId = `${el.id}_${generateRandomString(6)}`;
                el.id = newId;
            }
        });
    });
}

/**
 * Utility to find element by partial ID match
 * This can be used by testers to work around dynamic IDs
 */
window.findByPartialId = function(partialId) {
    return document.querySelector(`[id*="${partialId}"]`);
};

/**
 * Get all elements with dynamic IDs (for debugging)
 */
window.getDynamicElements = function() {
    const elements = [];
    document.querySelectorAll('[id]').forEach(el => {
        if (el.id.match(/_[a-z0-9]{6}$/)) {
            elements.push({
                id: el.id,
                tagName: el.tagName,
                text: el.textContent.substring(0, 50)
            });
        }
    });
    return elements;
};
