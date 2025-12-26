/**
 * SoulShield DOM Utilities Module
 * Provides safe DOM manipulation with Trusted Types support
 */
(function() {
    'use strict';

    // Create Trusted Types policy if supported
    let policy = null;
    if (window.trustedTypes && trustedTypes.createPolicy) {
        try {
            policy = trustedTypes.createPolicy('soulshield-dom-policy', {
                createHTML: (input) => {
                    // Sanitize HTML before allowing it
                    return window.SoulShieldSanitize.sanitizeHTML(input);
                },
                createScriptURL: (input) => {
                    // Only allow same-origin script URLs
                    try {
                        const url = new URL(input, window.location.origin);
                        if (url.origin === window.location.origin) {
                            return input;
                        }
                    } catch (e) {}
                    throw new Error('Blocked script URL: ' + input);
                }
            });
        } catch (e) {
            console.warn('Failed to create Trusted Types policy:', e);
        }
    }

    /**
     * Safely set innerHTML with sanitization
     */
    function setSafeHTML(element, htmlString) {
        if (!element) return;

        if (policy) {
            element.innerHTML = policy.createHTML(htmlString);
        } else {
            // Fallback: sanitize without Trusted Types
            element.innerHTML = window.SoulShieldSanitize.sanitizeHTML(htmlString);
        }
    }

    /**
     * Safely append HTML content
     */
    function appendSafeHTML(element, htmlString) {
        if (!element) return;

        const tempDiv = document.createElement('div');
        if (policy) {
            tempDiv.innerHTML = policy.createHTML(htmlString);
        } else {
            tempDiv.innerHTML = window.SoulShieldSanitize.sanitizeHTML(htmlString);
        }

        while (tempDiv.firstChild) {
            element.appendChild(tempDiv.firstChild);
        }
    }

    /**
     * Create element with safe text content
     */
    function createTextElement(tagName, text, className) {
        const element = document.createElement(tagName);
        element.textContent = text;
        if (className) {
            element.className = className;
        }
        return element;
    }

    /**
     * Create element with safe HTML content
     */
    function createHTMLElement(tagName, html, className) {
        const element = document.createElement(tagName);
        setSafeHTML(element, html);
        if (className) {
            element.className = className;
        }
        return element;
    }

    /**
     * Safe insertAdjacentHTML wrapper
     */
    function insertSafeHTML(element, position, htmlString) {
        if (!element) return;

        const tempDiv = document.createElement('div');
        if (policy) {
            tempDiv.innerHTML = policy.createHTML(htmlString);
        } else {
            tempDiv.innerHTML = window.SoulShieldSanitize.sanitizeHTML(htmlString);
        }

        const fragment = document.createDocumentFragment();
        while (tempDiv.firstChild) {
            fragment.appendChild(tempDiv.firstChild);
        }

        switch (position) {
            case 'beforebegin':
                element.parentNode.insertBefore(fragment, element);
                break;
            case 'afterbegin':
                element.insertBefore(fragment, element.firstChild);
                break;
            case 'beforeend':
                element.appendChild(fragment);
                break;
            case 'afterend':
                element.parentNode.insertBefore(fragment, element.nextSibling);
                break;
        }
    }

    // Export to global scope
    window.SoulShieldDOM = {
        setSafeHTML: setSafeHTML,
        appendSafeHTML: appendSafeHTML,
        insertSafeHTML: insertSafeHTML,
        createTextElement: createTextElement,
        createHTMLElement: createHTMLElement,
        policy: policy
    };
})();

