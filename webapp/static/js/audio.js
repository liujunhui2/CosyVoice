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
            this.bindAudioControls();
        });
    }
    
    bindAudioControls() {
        // Play/Pause button
        const playPauseBtn = document.getElementById('play-pause-btn');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => {
                this.togglePlayPause();
            });
        }
        
        // Stop button
        const stopBtn = document.getElementById('stop-btn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => {
                this.stopAudio();
            });
        }
        
        // Rewind button
        const rewindBtn = document.getElementById('rewind-btn');
        if (rewindBtn) {
            rewindBtn.addEventListener('click', () => {
                this.rewindAudio();
            });
        }
        
        // Replay button
        const replayBtn = document.getElementById('replay-btn');
        if (replayBtn) {
            replayBtn.addEventListener('click', () => {
                this.replayAudio();
            });
        }
        
        // Progress bar click
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.addEventListener('click', (e) => {
                this.seekAudio(e);
            });
        }
        
        // Audio player events
        if (this.generatedPlayer) {
            this.generatedPlayer.addEventListener('play', () => {
                this.updatePlayPauseButton(true);
                audioLogger.info('Play started');
            });
            
            this.generatedPlayer.addEventListener('pause', () => {
                this.updatePlayPauseButton(false);
                audioLogger.info('Playback paused');
            });
            
            this.generatedPlayer.addEventListener('ended', () => {
                this.updatePlayPauseButton(false);
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
        }
    }
    
    togglePlayPause() {
        if (!this.generatedPlayer) return;
        
        if (this.generatedPlayer.paused) {
            this.generatedPlayer.play().catch(error => {
                console.error('Error playing audio:', error);
                audioLogger.error('Failed to play audio', error.message);
            });
        } else {
            this.generatedPlayer.pause();
        }
    }
    
    stopAudio() {
        if (!this.generatedPlayer) return;
        
        this.generatedPlayer.pause();
        this.generatedPlayer.currentTime = 0;
        this.updatePlayPauseButton(false);
        audioLogger.info('Audio stopped');
    }
    
    rewindAudio() {
        if (!this.generatedPlayer) return;
        
        // Rewind by 10 seconds or to beginning
        const newTime = Math.max(0, this.generatedPlayer.currentTime - 10);
        this.generatedPlayer.currentTime = newTime;
        audioLogger.info('Rewound 10 seconds', `to ${Math.floor(newTime)}s`);
    }
    
    replayAudio() {
        if (!this.generatedPlayer) return;
        
        this.generatedPlayer.currentTime = 0;
        this.generatedPlayer.play().catch(error => {
            console.error('Error replaying audio:', error);
            audioLogger.error('Failed to replay audio', error.message);
        });
        audioLogger.info('Audio replay started');
    }
    
    seekAudio(event) {
        if (!this.generatedPlayer || !this.generatedPlayer.duration) return;
        
        const progressBar = event.currentTarget;
        const rect = progressBar.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const percentage = clickX / rect.width;
        
        this.generatedPlayer.currentTime = percentage * this.generatedPlayer.duration;
    }
    
    updatePlayPauseButton(isPlaying) {
        const playPauseBtn = document.getElementById('play-pause-btn');
        if (!playPauseBtn) return;
        
        if (isPlaying) {
            playPauseBtn.innerHTML = '⏸️ Pause';
        } else {
            playPauseBtn.innerHTML = '▶️ Play';
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
