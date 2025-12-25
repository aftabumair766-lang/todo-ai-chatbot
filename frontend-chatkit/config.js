/**
 * OpenAI ChatKit Configuration
 *
 * Constitution Compliance: Frontend → OpenAI ChatKit (Principle: Technology Stack)
 *
 * This configuration connects ChatKit to the FastAPI backend.
 * Update these values based on your deployment environment.
 */

window.CHATKIT_CONFIG = {
    /**
     * Backend API URL
     * - Development: http://localhost:8000
     * - Production: https://your-domain.com
     */
    backendUrl: 'http://localhost:8000',

    /**
     * OpenAI API Key (Optional - if using client-side authentication)
     * For production, handle authentication server-side only.
     * Leave empty to use backend's OpenAI key.
     */
    openaiApiKey: '',

    /**
     * ChatKit Session Endpoint
     * Creates or retrieves chat session with JWT authentication
     */
    sessionEndpoint: '/api/chatkit/session',

    /**
     * Chat Endpoint
     * Sends messages and receives responses
     */
    chatEndpoint: '/api/chat',

    /**
     * Welcome Message
     * Displayed when user first opens the chat
     */
    welcomeMessage: `👋 Hello! I'm your AI-powered todo assistant.

I can help you manage your tasks using natural language. Try:
• "Add a task to buy groceries"
• "Show me all my tasks"
• "Complete task 1"
• "Delete the grocery task"
• "Update task 2 to 'Buy milk and eggs'"

What would you like to do?`,

    /**
     * Domain Allowlist Configuration
     * Required by OpenAI ChatKit for security
     *
     * Add all domains where ChatKit will be hosted:
     * - Development: localhost:3000, localhost:5173, etc.
     * - Production: yourdomain.com, www.yourdomain.com
     */
    allowedDomains: [
        'localhost:3000',
        'localhost:5173',
        'localhost:8080',
        '127.0.0.1:3000',
        '127.0.0.1:5173',
        '127.0.0.1:8080',
        // Add your production domains here:
        // 'yourdomain.com',
        // 'www.yourdomain.com',
        // 'app.yourdomain.com',
    ],

    /**
     * CORS Configuration
     * These origins are allowed to make requests to the backend
     */
    corsOrigins: [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:8080',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080',
        // Add your production origins here:
        // 'https://yourdomain.com',
        // 'https://www.yourdomain.com',
    ],

    /**
     * ChatKit UI Customization
     */
    theme: {
        primaryColor: '#667eea',
        secondaryColor: '#764ba2',
        backgroundColor: '#ffffff',
        textColor: '#1f2937',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    },

    /**
     * Feature Flags
     */
    features: {
        voiceInput: false,        // Voice input (future feature)
        fileUpload: false,        // File upload (future feature)
        markdown: true,           // Markdown rendering in messages
        codeHighlight: false,     // Code syntax highlighting
        typing: true,             // Show typing indicator
        timestamps: true,         // Show message timestamps
        avatars: true,            // Show user/assistant avatars
    },

    /**
     * Rate Limiting
     * Must match backend configuration
     */
    rateLimit: {
        maxRequestsPerMinute: 10,
        showWarning: true,        // Warn user when approaching limit
    },

    /**
     * Retry Configuration
     */
    retry: {
        maxRetries: 3,
        retryDelay: 1000,         // milliseconds
        backoff: 'exponential',   // exponential or linear
    },

    /**
     * Debug Mode
     * Set to true for development debugging
     */
    debug: true,

    /**
     * Analytics (Optional)
     */
    analytics: {
        enabled: false,
        trackingId: '',           // Google Analytics, Mixpanel, etc.
    }
};

// Validate configuration on load
(function validateConfig() {
    const config = window.CHATKIT_CONFIG;
    const warnings = [];

    // Check required fields
    if (!config.backendUrl) {
        warnings.push('⚠️ backendUrl is not configured');
    }

    if (!config.sessionEndpoint) {
        warnings.push('⚠️ sessionEndpoint is not configured');
    }

    if (!config.chatEndpoint) {
        warnings.push('⚠️ chatEndpoint is not configured');
    }

    // Check domain allowlist
    if (!config.allowedDomains || config.allowedDomains.length === 0) {
        warnings.push('⚠️ allowedDomains is empty - ChatKit may not work');
    }

    // Log warnings
    if (warnings.length > 0) {
        console.warn('ChatKit Configuration Issues:');
        warnings.forEach(w => console.warn(w));
    } else if (config.debug) {
        console.log('✅ ChatKit configuration validated successfully');
        console.log('Configuration:', config);
    }
})();
