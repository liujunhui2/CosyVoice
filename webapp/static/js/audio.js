/**
 * CosyVoice Web Demo - Audio Control Logic
 */

// Safe logger wrapper for audio module
const audioLogger = {
    info: (msg, data) => typeof logger !== 'undefined' ? logger.logAudioEvent(msg, data) : console.log(`[AUDIO] ${msg}`, data),
    success: (msg, data) => typeof logger !== 'undefined' ? logger.success(`Audio: ${msg}`, data) : console.log(`[AUDIO SUCCESS] ${msg}`, data),
    error: (msg, data) => typeof logger !== 'undefined' ? logger.error(`Audio: ${msg}`, data) : console.error(`[AUDIO ERROR] ${msg}`, data)
};

class AudioController {
    constructor() {
        this.generatedPlayer = null;
        this.initializeAudioControls();
    }
    
    initializeAudioControls() {
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.generatedPlayer = document.getElementById('generated-player');
            this.bindAudioEvents();
        });
    }
    
    bindAudioEvents() {
        // Audio player events for logging and monitoring
        if (this.generatedPlayer) {
            this.generatedPlayer.addEventListener('play', () => {
                audioLogger.info('Play started');
            });
            
            this.generatedPlayer.addEventListener('pause', () => {
                audioLogger.info('Playback paused');
            });
            
            this.generatedPlayer.addEventListener('ended', () => {
                audioLogger.info('Playback completed');
            });
            
            this.generatedPlayer.addEventListener('error', (e) => {
                audioLogger.error('Playback error', e.error);
            });
            
            this.generatedPlayer.addEventListener('loadstart', () => {
                audioLogger.info('Loading audio...');
            });
            
            this.generatedPlayer.addEventListener('canplay', () => {
                audioLogger.info('Audio ready to play');
            });
            
            this.generatedPlayer.addEventListener('loadedmetadata', () => {
                audioLogger.info('Audio metadata loaded', `Duration: ${Math.floor(this.generatedPlayer.duration)}s`);
            });
        }
    }
}

// Streaming Audio Handler
class StreamingAudioHandler {
    constructor() {
        this.audioContext = null;
        this.sourceBuffer = null;
        this.audioQueue = [];
        this.isPlaying = false;
    }
    
    async initializeAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            audioLogger.success('Audio context initialized for streaming');
            return true;
        } catch (error) {
            console.error('Failed to initialize audio context:', error);
            audioLogger.error('Failed to initialize audio context', error.message);
            return false;
        }
    }
    
    async handleStreamingAudio(response) {
        if (!await this.initializeAudioContext()) {
            throw new Error('Audio context not supported');
        }
        
        const reader = response.body.getReader();
        const chunks = [];
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                chunks.push(value);
                
                // For streaming playback, you would process chunks here
                // This is a simplified version that collects all chunks
            }
            
            // Combine all chunks
            const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
            const combinedArray = new Uint8Array(totalLength);
            let offset = 0;
            
            for (const chunk of chunks) {
                combinedArray.set(chunk, offset);
                offset += chunk.length;
            }
            
            // Create blob and return URL
            const audioBlob = new Blob([combinedArray], { type: 'audio/wav' });
            return URL.createObjectURL(audioBlob);
            
        } finally {
            reader.releaseLock();
        }
    }
}

// Initialize audio controller
const audioController = new AudioController();
const streamingHandler = new StreamingAudioHandler();

// Export for use in main app
window.AudioController = AudioController;
window.StreamingAudioHandler = StreamingAudioHandler;
