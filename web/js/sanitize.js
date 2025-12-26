/**
 * SoulShield HTML Sanitization Module
 * Prevents XSS attacks by sanitizing user-generated content
 */
(function() {
    'use strict';

    // Allowed HTML tags and their permitted attributes
    const ALLOWED_TAGS = {
        'b': [],
        'i': [],
        'em': [],
        'strong': [],
        'a': ['href'],
        'p': [],
        'br': [],
        'ul': [],
        'ol': [],
        'li': [],
        'blockquote': [],
        'code': [],
        'pre': []
    };

    // Allowed URL protocols for links
    const ALLOWED_PROTOCOLS = ['http:', 'https:', 'mailto:'];

    /**
     * Sanitize HTML string to prevent XSS
     */
    function sanitizeHTML(html) {
        if (!html || typeof html !== 'string') {
            return '';
        }

        const doc = new DOMParser().parseFromString(html, 'text/html');
        const sanitizedBody = sanitizeNode(doc.body);
        return sanitizedBody.innerHTML;
    }

    /**
     * Recursively sanitize DOM node
     */
    function sanitizeNode(node) {
        const fragment = document.createDocumentFragment();

        for (const child of Array.from(node.childNodes)) {
            if (child.nodeType === Node.TEXT_NODE) {
                // Text nodes are safe
                fragment.appendChild(document.createTextNode(child.textContent));
            } else if (child.nodeType === Node.ELEMENT_NODE) {
                const tagName = child.nodeName.toLowerCase();

                if (ALLOWED_TAGS.hasOwnProperty(tagName)) {
                    // Create sanitized element
                    const sanitizedElement = document.createElement(tagName);

                    // Copy only allowed attributes
                    const allowedAttrs = ALLOWED_TAGS[tagName];
                    for (const attr of allowedAttrs) {
                        if (child.hasAttribute(attr)) {
                            const value = child.getAttribute(attr);
                            
                            // Validate href URLs
                            if (attr === 'href') {
                                try {
                                    const url = new URL(value, window.location.origin);
                                    if (ALLOWED_PROTOCOLS.includes(url.protocol)) {
                                        sanitizedElement.setAttribute(attr, value);
                                    }
                                } catch (e) {
                                    // Invalid URL, skip
                                }
                            } else {
                                sanitizedElement.setAttribute(attr, value);
                            }
                        }
                    }

                    // Recursively sanitize children
                    sanitizedElement.appendChild(sanitizeNode(child));
                    fragment.appendChild(sanitizedElement);
                } else {
                    // Tag not allowed, but include text content
                    fragment.appendChild(sanitizeNode(child));
                }
            }
        }

        const container = document.createElement('div');
        container.appendChild(fragment);
        return container;
    }

    /**
     * Escape HTML entities (for plain text display)
     */
    function escapeHTML(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Format message text with safe rendering
     * Converts markdown-like syntax to safe HTML
     */
    function formatMessage(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }

        // Escape HTML first
        let safe = escapeHTML(text);

        // Convert double newlines to paragraphs
        safe = safe.replace(/\n\n/g, '</p><p>');
        
        // Convert single newlines to breaks
        safe = safe.replace(/\n/g, '<br>');
        
        // Convert **bold** to <strong>
        safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *italic* to <em>
        safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');

        return '<p>' + safe + '</p>';
    }

    // Export to global scope
    window.SoulShieldSanitize = {
        sanitizeHTML: sanitizeHTML,
        escapeHTML: escapeHTML,
        formatMessage: formatMessage
    };
})();

