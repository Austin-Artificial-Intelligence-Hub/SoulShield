# Enhanced Memory with Privacy

## Current State
- ✅ Session-based memory (works within one conversation)
- ✅ Auto-deletion after 30 days
- ✅ Encrypted storage

## Enhanced User Memory Options

### Option 1: Anonymous User IDs (Recommended)
```
User provides: Email/Username → Hashed to anonymous ID
Storage: Hash(email) → conversation history
Privacy: No way to reverse hash to original email
```

### Option 2: Client-Side User IDs
```
User creates: Local username in browser
Storage: User-chosen ID → conversation history  
Privacy: User controls their own identifier
```

### Option 3: Temporary User Sessions
```
User gets: 7-day persistent session token
Storage: Token → conversation history
Privacy: Token expires, no permanent tracking
```

## Privacy Enhancements for User Memory

1. **Separate User Table**
   - UserID (hashed) → Conversation sessions
   - No personal data stored

2. **Conversation Isolation**
   - Each conversation still gets unique session ID
   - User can have multiple conversations
   - No cross-conversation data leakage

3. **Enhanced Encryption**
   - User-specific encryption keys
   - Even admins can't read conversations

4. **Data Controls**
   - User can delete all their data
   - User can export their data
   - Configurable retention per user

## Implementation Plan

Would you like me to implement:
- [ ] Anonymous hashed user IDs
- [ ] Client-side user management
- [ ] Enhanced encryption
- [ ] User data controls (delete/export)

Which approach interests you most?