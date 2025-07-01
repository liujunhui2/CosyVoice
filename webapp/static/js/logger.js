/**
 * Logger utility for the CosyVoice Web Application
 * Provides console-style logging with different levels and timestamps
 */

class Logger {
    constructor() {
        this.logContainer = null;
        this.logContent = null;
        this.isCollapsed = false;
        this.maxEntries = 100; // Maximum number of log entries to keep
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupLogger());
        } else {
            this.setupLogger();
        }
    }

    setupLogger() {
        this.logContainer = document.getElementById('log-container');
        this.logContent = document.getElementById('log-content');
        
        if (!this.logContainer || !this.logContent) {
            console.warn('Logger: Log container elements not found');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();
        
        // Clear the initial placeholder log entry
        this.logContent.innerHTML = '';
        
        // Add initial log entry
        this.info('Logger initialized successfully');
    }

    setupEventListeners() {
        const clearBtn = document.getElementById('clear-log-btn');
        const toggleBtn = document.getElementById('toggle-log-btn');
        const testBtn = document.getElementById('test-log-btn');
        const testAudioBtn = document.getElementById('test-audio-btn');

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }

        if (testBtn) {
            testBtn.addEventListener('click', () => this.testLogging());
        }

        if (testAudioBtn) {
            testAudioBtn.addEventListener('click', () => this.testAudio());
        }
    }

    /**
     * Add a log entry with specified level
     * @param {string} level - Log level (info, success, warning, error, debug)
     * @param {string} message - Log message
     * @param {Object} data - Optional data object to display
     */
    log(level, message, data = null) {
        if (!this.logContent) {
            console.warn('Logger: logContent not available, falling back to console');
            console.log(`[${level.toUpperCase()}] ${message}`, data);
            return;
        }

        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${level}`;

        let messageText = message;
        if (data) {
            if (typeof data === 'object') {
                messageText += ` | Data: ${JSON.stringify(data, null, 2)}`;
            } else {
                messageText += ` | ${data}`;
            }
        }

        logEntry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-message">${this.escapeHtml(messageText)}</span>
        `;

        // Add to log content
        this.logContent.appendChild(logEntry);

        // Limit number of entries
        this.limitEntries();

        // Auto-scroll to bottom
        this.scrollToBottom();

        // Also log to browser console for debugging
        const consoleMethod = level === 'error' ? 'error' : 
                             level === 'warning' ? 'warn' : 
                             level === 'debug' ? 'debug' : 'log';
        console[consoleMethod](`[CosyVoice Logger ${level.toUpperCase()}] ${message}`, data || '');
    }

    /**
     * Log info message
     * @param {string} message 
     * @param {Object} data 
     */
    info(message, data = null) {
        this.log('info', message, data);
    }

    /**
     * Log success message
     * @param {string} message 
     * @param {Object} data 
     */
    success(message, data = null) {
        this.log('success', message, data);
    }

    /**
     * Log warning message
     * @param {string} message 
     * @param {Object} data 
     */
    warning(message, data = null) {
        this.log('warning', message, data);
    }

    /**
     * Log error message
     * @param {string} message 
     * @param {Object} data 
     */
    error(message, data = null) {
        this.log('error', message, data);
    }

    /**
     * Log debug message
     * @param {string} message 
     * @param {Object} data 
     */
    debug(message, data = null) {
        this.log('debug', message, data);
    }

    /**
     * Clear all log entries
     */
    clear() {
        if (this.logContent) {
            this.logContent.innerHTML = '';
            this.info('Log cleared');
        }
    }

    /**
     * Toggle log visibility
     */
    toggle() {
        if (!this.logContainer) return;

        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            this.logContainer.classList.add('collapsed');
        } else {
            this.logContainer.classList.remove('collapsed');
        }

        const toggleBtn = document.getElementById('toggle-log-btn');
        if (toggleBtn) {
            toggleBtn.textContent = this.isCollapsed ? '📖 Show Log' : '📖 Hide Log';
        }
    }

    /**
     * Scroll log to bottom
     */
    scrollToBottom() {
        if (this.logContainer && !this.isCollapsed) {
            this.logContainer.scrollTop = this.logContainer.scrollHeight;
        }
    }

    /**
     * Limit number of log entries to prevent memory issues
     */
    limitEntries() {
        if (!this.logContent) return;

        const entries = this.logContent.querySelectorAll('.log-entry');
        if (entries.length > this.maxEntries) {
            const entriesToRemove = entries.length - this.maxEntries;
            for (let i = 0; i < entriesToRemove; i++) {
                entries[i].remove();
            }
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text 
     * @returns {string}
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Log API request
     * @param {string} method 
     * @param {string} url 
     * @param {Object} data 
     */
    logApiRequest(method, url, data = null) {
        this.debug(`API Request: ${method} ${url}`, data);
    }

    /**
     * Log API response
     * @param {string} method 
     * @param {string} url 
     * @param {number} status 
     * @param {Object} data 
     */
    logApiResponse(method, url, status, data = null) {
        const level = status >= 400 ? 'error' : status >= 300 ? 'warning' : 'success';
        this.log(level, `API Response: ${method} ${url} - ${status}`, data);
    }

    /**
     * Log audio event
     * @param {string} event 
     * @param {string} details 
     */
    logAudioEvent(event, details = '') {
        this.info(`Audio: ${event}${details ? ' - ' + details : ''}`);
    }

    /**
     * Test logging functionality
     */
    testLogging() {
        this.info('Testing logger functionality...');
        this.success('This is a success message');
        this.warning('This is a warning message');
        this.error('This is an error message');
        this.debug('This is a debug message');
        this.logAudioEvent('Test audio event', 'with details');
        this.info('Logger test completed');
    }

    /**
     * Test audio playback functionality
     */
    async testAudio() {
        this.info('Testing audio playback...');
        try {
            const response = await fetch('/api/test-audio');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const audioBlob = await response.blob();
            this.info(`Test audio received: ${audioBlob.size} bytes, type: ${audioBlob.type}`);

            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            audio.addEventListener('canplay', () => {
                this.success('Test audio ready to play');
            });
            
            audio.addEventListener('error', (e) => {
                this.error('Test audio playback error', e.error);
            });
            
            audio.addEventListener('ended', () => {
                this.info('Test audio playback completed');
                URL.revokeObjectURL(audioUrl);
            });

            await audio.play();
            this.info('Test audio playback started');
            
        } catch (error) {
            this.error('Test audio failed', error.message);
        }
    }
}

// Create global logger instance
const logger = new Logger();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Logger;
}
