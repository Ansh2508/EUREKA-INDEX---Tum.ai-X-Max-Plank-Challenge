/**
 * Security utility functions to prevent XSS and injection attacks
 */

// HTML escaping to prevent XSS
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') {
        return unsafe;
    }
    
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/\//g, "&#x2F;");
}

// Safe innerHTML replacement
function setInnerHTMLSafe(element, htmlContent) {
    // Create a temporary element to parse and sanitize
    const temp = document.createElement('div');
    temp.innerHTML = htmlContent;
    
    // Remove potentially dangerous elements and attributes
    const dangerousElements = ['script', 'iframe', 'object', 'embed', 'link', 'style'];
    const dangerousAttributes = ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'onsubmit'];
    
    dangerousElements.forEach(tagName => {
        const elements = temp.querySelectorAll(tagName);
        elements.forEach(el => el.remove());
    });
    
    // Remove dangerous attributes from all elements
    const allElements = temp.querySelectorAll('*');
    allElements.forEach(el => {
        dangerousAttributes.forEach(attr => {
            if (el.hasAttribute(attr)) {
                el.removeAttribute(attr);
            }
        });
        
        // Remove javascript: protocols
        ['href', 'src'].forEach(attr => {
            const value = el.getAttribute(attr);
            if (value && value.toLowerCase().startsWith('javascript:')) {
                el.removeAttribute(attr);
            }
        });
    });
    
    element.innerHTML = temp.innerHTML;
}

// Input validation
function validateInput(input, maxLength = 10000) {
    if (!input || typeof input !== 'string') {
        throw new Error('Invalid input: must be a non-empty string');
    }
    
    if (input.length > maxLength) {
        throw new Error(`Input too long: maximum ${maxLength} characters allowed`);
    }
    
    // Check for potentially malicious patterns
    const maliciousPatterns = [
        /<script/i,
        /javascript:/i,
        /on\w+\s*=/i,
        /<iframe/i,
        /<object/i,
        /<embed/i
    ];
    
    for (const pattern of maliciousPatterns) {
        if (pattern.test(input)) {
            throw new Error('Input contains potentially malicious content');
        }
    }
    
    return input.trim();
}

// Safe text content setting
function setTextContentSafe(element, text) {
    element.textContent = escapeHtml(text);
}

// Safe JSON.stringify with validation
function safeJSONStringify(obj) {
    try {
        // Validate object structure
        if (obj && typeof obj === 'object') {
            for (const [key, value] of Object.entries(obj)) {
                if (typeof value === 'string') {
                    validateInput(value);
                }
            }
        }
        
        return JSON.stringify(obj);
    } catch (error) {
        throw new Error('Failed to serialize data safely: ' + error.message);
    }
}

// Export functions for use in other scripts
window.SecurityUtils = {
    escapeHtml,
    setInnerHTMLSafe,
    validateInput,
    setTextContentSafe,
    safeJSONStringify
};
