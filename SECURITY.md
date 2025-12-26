# SoulShield Security Architecture

This document details the comprehensive security features implemented in SoulShield to protect user privacy and prevent data breaches.

## 🔐 Client-Side Encryption

### AES-256-GCM Encryption
All messages can be encrypted in the browser before transmission using industry-standard encryption:

- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Salt**: Cryptographically random 16-byte salt per message
- **IV**: Random 12-byte initialization vector per encryption

```javascript
// How encryption works (web/js/encryption.js)
const key = await deriveKey(password, salt);  // PBKDF2
const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    message
);
```

### Zero-Knowledge Architecture
- Only the user's password can decrypt their messages
- Server never sees plaintext messages or encryption keys
- Even database administrators cannot read encrypted content

## 🛡️ XSS Protection

### Content Security Policy (CSP)
The web UI implements a strict Content Security Policy:

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
    img-src 'self' data:;
    connect-src 'self' https://*.amazonaws.com https://*.execute-api.amazonaws.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
">
```

**Key protections:**
- No inline scripts allowed
- No external script sources except 'self'
- No iframe embedding (clickjacking protection)
- Restricted form submissions

### Trusted Types
Modern browsers support Trusted Types for DOM-level XSS prevention:

```javascript
// web/js/dom-utils.js
const policy = trustedTypes.createPolicy('soulshield-dom-policy', {
    createHTML: (input) => sanitizeHTML(input),
    createScriptURL: (input) => validateURL(input)
});
```

### HTML Sanitization
All user-generated content is sanitized before rendering:

```javascript
// web/js/sanitize.js
const ALLOWED_TAGS = {
    'b': [], 'i': [], 'em': [], 'strong': [],
    'a': ['href'], 'p': [], 'br': [],
    'ul': [], 'ol': [], 'li': [],
    'blockquote': [], 'code': [], 'pre': []
};

function sanitizeHTML(html) {
    // Parse and rebuild with only allowed tags/attributes
}
```

### No Inline Event Handlers
All event handlers are attached via JavaScript, not inline HTML:

```javascript
// Bad (vulnerable to XSS)
<button onclick="sendMessage()">Send</button>

// Good (CSP-compliant)
document.getElementById('sendBtn').addEventListener('click', sendMessage);
```

## 🔒 Server-Side Security

### Password Hashing
User passwords are never stored in plaintext:

```python
# PBKDF2-HMAC-SHA256 with 100,000 iterations
import hashlib

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt.hex() + key.hex()
```

### Token-Based Authentication
- Tokens expire after 24 hours
- Token format: `base64(username:timestamp)`
- Validated on every API request

### AWS Security
- **DynamoDB**: AWS-managed AES-256 encryption at rest
- **API Gateway**: HTTPS-only, API key required
- **Lambda**: IAM roles with least-privilege access
- **CloudWatch**: Chat content excluded from logs

### Data Retention
- All data automatically deleted after 30 days (TTL)
- Users can manually clear their data
- No backups containing user content

## 👀 Bystander Safety

SoulShield is designed for users who may be monitored (e.g., domestic violence situations):

### Privacy Context Detection
The routing agent detects if a user may not have privacy:

```json
{
    "privacy_context": "bystander_possible"
}
```

Triggers include:
- "He might check my phone"
- "Someone is nearby"
- "I can't talk openly"
- Any hint of surveillance or coercion

### Bystander-Safe Language
When privacy is unknown or compromised:

**DO:**
- Use neutral, everyday wellness wording
- Keep responses short and calm
- Offer yes/no or single-choice options
- Focus on grounding and self-regulation

**DON'T:**
- Use explicit labels (trafficking, abuse, escape)
- Mention emergency numbers prominently
- Ask for identifying details
- Escalate or suggest immediate action

## 🧪 Security Testing

### Recommended Tests
1. **XSS Injection**: Try injecting `<script>alert('xss')</script>` in messages
2. **CSP Bypass**: Verify inline scripts don't execute
3. **Encryption**: Verify server only stores encrypted content
4. **Password Cracking**: Ensure hashes resist rainbow tables

### Vulnerability Reporting
If you discover a security vulnerability:
1. **DO NOT** create a public GitHub issue
2. Email security concerns to the maintainers privately
3. Allow 90 days for patch before public disclosure

## 📋 Security Checklist

- [ ] CSP headers active (check DevTools > Network > Response Headers)
- [ ] No inline scripts in HTML source
- [ ] Passwords hashed with PBKDF2 (100k iterations)
- [ ] API requires authentication
- [ ] DynamoDB encryption enabled
- [ ] HTTPS enforced on API Gateway
- [ ] Data TTL configured for auto-deletion
- [ ] No sensitive data in CloudWatch logs

## 🔄 Future Enhancements

Planned security improvements:
- [ ] AWS KMS Customer-Managed Keys for DynamoDB
- [ ] End-to-end encryption with key exchange
- [ ] Hardware security key (WebAuthn) support
- [ ] Subresource Integrity for all external resources
- [ ] Security audit by third party

