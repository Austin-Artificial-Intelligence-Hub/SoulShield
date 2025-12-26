/**
 * SoulShield Main Application
 * Trauma-informed support companion with security features
 */
(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        get apiUrl() { return window.SOULSHIELD_CONFIG?.apiUrl || 'https://pypwr35xf3.execute-api.us-east-1.amazonaws.com/prod'; },
        get apiKey() { return window.SOULSHIELD_CONFIG?.apiKey || ''; }
    };

    // Application state
    const state = {
        isLoggedIn: false,
        username: '',
        token: '',
        sessionId: generateSessionId(),
        messages: [],
        isRegisterMode: false,
        currentPage: 'chat'
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        const savedState = localStorage.getItem('soulshield_state');
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                if (parsed.token) {
                    state.token = parsed.token;
                    state.username = parsed.username || '';
                    state.isLoggedIn = true;
                    onLoginSuccess();
                }
            } catch (e) {
                console.error('Failed to restore session:', e);
            }
        }

        setupEventListeners();
        autoResizeTextarea();
    }

    function setupEventListeners() {
        // Auth form
        const authForm = document.getElementById('authForm');
        if (authForm) {
            authForm.addEventListener('submit', handleAuth);
        }

        // Chat input
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keydown', handleKeyDown);
        }

        // Send button
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', sendMessage);
        }

        // Logout button
        const logoutBtn = document.querySelector('.btn-logout');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }

        // New session button
        const newSessionBtn = document.querySelector('.btn-new-session');
        if (newSessionBtn) {
            newSessionBtn.addEventListener('click', newSession);
        }

        // Auth toggle link
        const authToggleLink = document.getElementById('authToggleLink');
        if (authToggleLink) {
            authToggleLink.addEventListener('click', toggleAuthMode);
        }

        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', handleNavigation);
        });

        // Quick action buttons
        setupQuickActionListeners();
    }

    function generateSessionId() {
        return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    function saveState() {
        localStorage.setItem('soulshield_state', JSON.stringify({
            username: state.username,
            token: state.token
        }));
    }

    // Navigation
    function handleNavigation(e) {
        e.preventDefault();
        const page = e.target.getAttribute('data-page');
        if (page) {
            showPage(page);
        }
    }

    function showPage(page) {
        state.currentPage = page;
        const mainContent = document.getElementById('mainContent');
        const chatContainer = document.querySelector('.chat-container');
        const sidebar = document.getElementById('sidebar');
        
        // Hide modal pages
        document.querySelectorAll('.page-modal').forEach(m => m.style.display = 'none');
        
        if (page === 'chat') {
            if (chatContainer) chatContainer.style.display = 'flex';
            if (sidebar && state.isLoggedIn) sidebar.style.display = 'flex';
        } else {
            if (chatContainer) chatContainer.style.display = 'none';
            if (sidebar) sidebar.style.display = 'none';
            const pageModal = document.getElementById(page + 'Page');
            if (pageModal) pageModal.style.display = 'flex';
        }
    }

    // Authentication
    function toggleAuthMode(e) {
        if (e) e.preventDefault();
        state.isRegisterMode = !state.isRegisterMode;
        
        const authTitle = document.getElementById('authTitle');
        const authSubtitle = document.getElementById('authSubtitle');
        const authBtn = document.getElementById('authBtn');
        const authToggleText = document.getElementById('authToggleText');
        const authToggleLinkEl = document.getElementById('authToggleLink');
        const authError = document.getElementById('authError');

        if (authTitle) authTitle.textContent = state.isRegisterMode ? 'Create Account' : 'Welcome Back';
        if (authSubtitle) authSubtitle.textContent = state.isRegisterMode ? 'Join us on your wellness journey' : 'Sign in to continue your journey';
        if (authBtn) authBtn.textContent = state.isRegisterMode ? 'Create Account' : 'Sign In';
        if (authToggleText) authToggleText.textContent = state.isRegisterMode ? 'Already have an account?' : "Don't have an account?";
        if (authToggleLinkEl) authToggleLinkEl.textContent = state.isRegisterMode ? 'Sign in' : 'Create one';
        if (authError) authError.style.display = 'none';
    }

    async function handleAuth(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const btn = document.getElementById('authBtn');
        const error = document.getElementById('authError');

        if (!username || !password) {
            showError(error, 'Please enter username and password');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Please wait...';
        error.style.display = 'none';

        try {
            const endpoint = state.isRegisterMode ? '/auth/register' : '/auth/login';
            const response = await fetch(CONFIG.apiUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': CONFIG.apiKey
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                if (state.isRegisterMode) {
                    state.isRegisterMode = false;
                    toggleAuthMode();
                    showSuccess(error, 'Account created! Please sign in.');
                } else {
                    state.token = data.token;
                    state.username = username;
                    state.isLoggedIn = true;
                    saveState();
                    onLoginSuccess();
                }
            } else {
                showError(error, data.error || 'Something went wrong');
            }
        } catch (err) {
            showError(error, 'Connection error. Please try again.');
        }

        btn.disabled = false;
        btn.textContent = state.isRegisterMode ? 'Create Account' : 'Sign In';
    }

    function showError(element, message) {
        if (element) {
            element.style.display = 'block';
            element.style.background = '#FEE2E2';
            element.style.color = '#991B1B';
            element.textContent = message;
        }
    }

    function showSuccess(element, message) {
        if (element) {
            element.style.display = 'block';
            element.style.background = '#D1FAE5';
            element.style.color = '#065F46';
            element.textContent = message;
        }
    }

    function onLoginSuccess() {
        const authModal = document.getElementById('authModal');
        const sidebar = document.getElementById('sidebar');
        const userInfo = document.getElementById('userInfo');
        const userName = document.getElementById('userName');
        const sessionIdDisplay = document.getElementById('sessionIdDisplay');

        if (authModal) authModal.style.display = 'none';
        if (sidebar) sidebar.style.display = 'flex';
        if (userInfo) userInfo.style.display = 'flex';
        if (userName) userName.textContent = state.username;
        if (sessionIdDisplay) sessionIdDisplay.textContent = state.sessionId.substr(0, 8) + '...';
    }

    function logout() {
        state.isLoggedIn = false;
        state.username = '';
        state.token = '';
        state.sessionId = generateSessionId();
        state.messages = [];
        state.isRegisterMode = false;

        localStorage.removeItem('soulshield_state');

        const authModal = document.getElementById('authModal');
        const sidebar = document.getElementById('sidebar');
        const userInfo = document.getElementById('userInfo');
        const messagesContainer = document.getElementById('messagesContainer');
        const messageCount = document.getElementById('messageCount');

        if (authModal) authModal.style.display = 'flex';
        if (sidebar) sidebar.style.display = 'none';
        if (userInfo) userInfo.style.display = 'none';
        if (messageCount) messageCount.textContent = '0';
        
        if (messagesContainer) {
            messagesContainer.innerHTML = getWelcomeHTML();
            setupQuickActionListeners();
        }
    }

    function newSession() {
        state.sessionId = generateSessionId();
        state.messages = [];

        const sessionIdDisplay = document.getElementById('sessionIdDisplay');
        const messageCount = document.getElementById('messageCount');
        const messagesContainer = document.getElementById('messagesContainer');

        if (sessionIdDisplay) sessionIdDisplay.textContent = state.sessionId.substr(0, 8) + '...';
        if (messageCount) messageCount.textContent = '0';
        
        if (messagesContainer) {
            messagesContainer.innerHTML = getNewSessionHTML();
            setupQuickActionListeners();
        }
    }

    function getWelcomeHTML() {
        return `
            <div class="welcome-state" id="welcomeState">
                <div class="welcome-icon">🌿</div>
                <h2>Welcome to SoulShield</h2>
                <p>I'm here to listen and support you. Take your time — there's no rush.</p>
                <div class="quick-actions">
                    <button class="quick-action" data-message="I need someone to talk to">I need someone to talk to</button>
                    <button class="quick-action" data-message="I feel stressed lately">I'm feeling stressed</button>
                    <button class="quick-action" data-message="Help me calm down">Help me calm down</button>
                </div>
            </div>
        `;
    }

    function getNewSessionHTML() {
        return `
            <div class="welcome-state" id="welcomeState">
                <div class="welcome-icon">✨</div>
                <h2>Fresh Start</h2>
                <p>A new session, a new moment. I'm here whenever you're ready.</p>
                <div class="quick-actions">
                    <button class="quick-action" data-message="I need someone to talk to">I need someone to talk to</button>
                    <button class="quick-action" data-message="I feel stressed lately">I'm feeling stressed</button>
                    <button class="quick-action" data-message="Help me calm down">Help me calm down</button>
                </div>
            </div>
        `;
    }

    function setupQuickActionListeners() {
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', function() {
                const message = this.getAttribute('data-message') || this.textContent;
                sendQuickMessage(message);
            });
        });
    }

    // Chat functionality
    function sendQuickMessage(message) {
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = message;
            sendMessage();
        }
    }

    async function sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input?.value.trim();
        if (!message) return;

        // Hide welcome state
        const welcome = document.getElementById('welcomeState');
        if (welcome) welcome.remove();

        // Add user message to UI
        addMessage('user', message);
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const response = await fetch(CONFIG.apiUrl + '/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': CONFIG.apiKey
                },
                body: JSON.stringify({
                    message,
                    sessionId: state.sessionId,
                    token: state.token
                })
            });

            removeTypingIndicator(typingId);

            if (response.ok) {
                const data = await response.json();
                addMessage('assistant', data.response, data.options);
            } else if (response.status === 401) {
                addMessage('assistant', 'Your session has expired. Please log in again.');
                setTimeout(logout, 2000);
            } else {
                addMessage('assistant', 'I apologize, but I encountered an issue. Please try again.');
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            addMessage('assistant', 'Connection error. Please check your internet and try again.');
        }

        const messageCount = document.getElementById('messageCount');
        if (messageCount) messageCount.textContent = state.messages.length;
    }

    function addMessage(role, content, options = []) {
        const container = document.getElementById('messagesContainer');
        if (!container) return;

        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        state.messages.push({ role, content, time });

        // Format content safely
        const escapedContent = escapeHTML(content);
        const formattedContent = escapedContent
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        // Create options HTML - styled as clickable buttons
        let optionsHTML = '';
        if (options && options.length > 0) {
            optionsHTML = `
                <div class="message-options">
                    ${options.map(opt => `<button class="option-btn" data-option="${escapeHTML(opt)}">${escapeHTML(opt)}</button>`).join('')}
                </div>
            `;
        }

        // Single avatar per message
        const avatar = role === 'user' ? '👤' : '💚';

        const messageHTML = `
            <div class="message ${role}">
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">
                    <div class="message-bubble"><p>${formattedContent}</p></div>
                    ${optionsHTML}
                    <div class="message-time">${escapeHTML(time)}</div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', messageHTML);
        container.scrollTop = container.scrollHeight;

        // Add click handlers for option buttons
        container.querySelectorAll('.option-btn:not([data-bound])').forEach(btn => {
            btn.setAttribute('data-bound', 'true');
            btn.addEventListener('click', function() {
                sendQuickMessage(this.getAttribute('data-option'));
            });
        });
    }

    function escapeHTML(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showTypingIndicator() {
        const container = document.getElementById('messagesContainer');
        if (!container) return null;

        const id = 'typing-' + Date.now();
        const html = `
            <div class="message assistant typing-message" id="${id}">
                <div class="message-avatar">💚</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div class="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', html);
        container.scrollTop = container.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        if (!id) return;
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Helpers
    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    function autoResizeTextarea() {
        const textarea = document.getElementById('chatInput');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 150) + 'px';
            });
        }
    }

    // Expose minimal API
    window.SoulShieldApp = {
        showPage: showPage,
        newSession: newSession
    };
})();
