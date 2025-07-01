/**
 * CosyVoice Web Demo - Main Application Logic
 */

// Safe logger wrapper
const safeLogger = {
    info: (msg, data) => typeof logger !== 'undefined' ? logger.info(msg, data) : console.log(`[INFO] ${msg}`, data),
    success: (msg, data) => typeof logger !== 'undefined' ? logger.success(msg, data) : console.log(`[SUCCESS] ${msg}`, data),
    warning: (msg, data) => typeof logger !== 'undefined' ? logger.warning(msg, data) : console.warn(`[WARNING] ${msg}`, data),
    error: (msg, data) => typeof logger !== 'undefined' ? logger.error(msg, data) : console.error(`[ERROR] ${msg}`, data),
    debug: (msg, data) => typeof logger !== 'undefined' ? logger.debug(msg, data) : console.debug(`[DEBUG] ${msg}`, data)
};

class CosyVoiceApp {
    constructor() {
        this.referenceAudios = [];
        this.selectedReferenceId = null;
        this.isGenerating = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadReferenceAudios();
    }
    
    initializeElements() {
        // Form elements
        this.referenceSelect = document.getElementById('reference-select');
        this.transcriptDisplay = document.getElementById('transcript-display');
        this.textInput = document.getElementById('text-input');
        this.generateBtn = document.getElementById('generate-btn');
        this.loadingSpinner = document.getElementById('loading-spinner');
        
        // Audio elements
        this.referencePlayer = document.getElementById('reference-player');
        this.referenceContainer = document.getElementById('reference-audio-container');
        this.noReferenceMessage = document.getElementById('no-reference-message');
        this.generatedPlayer = document.getElementById('generated-player');
        this.generatedSection = document.getElementById('generated-audio-section');
    }
    
    bindEvents() {
        // Reference audio selection
        this.referenceSelect.addEventListener('change', (e) => {
            this.onReferenceAudioChange(e.target.value);
        });
        
        // Text input validation
        this.textInput.addEventListener('input', () => {
            this.validateForm();
        });
        
        // Generate button
        this.generateBtn.addEventListener('click', () => {
            this.generateVoice();
        });
        
        // Generated audio events
        this.generatedPlayer.addEventListener('loadedmetadata', () => {
            this.updateAudioProgress();
        });
        
        this.generatedPlayer.addEventListener('timeupdate', () => {
            this.updateAudioProgress();
        });
    }
    
    async loadReferenceAudios() {
        try {
            safeLogger.info('Loading reference audios...');
            const response = await fetch('/api/reference-audios');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.referenceAudios = await response.json();
            this.populateReferenceSelect();
            safeLogger.success(`Loaded ${this.referenceAudios.length} reference audios`);
            
        } catch (error) {
            console.error('Failed to load reference audios:', error);
            safeLogger.error('Failed to load reference audios. Please refresh the page.', error.message);
            this.referenceSelect.innerHTML = '<option value="">Error loading audios</option>';
        }
    }
    
    populateReferenceSelect() {
        this.referenceSelect.innerHTML = '<option value="">Select a reference audio...</option>';
        
        this.referenceAudios.forEach(audio => {
            const option = document.createElement('option');
            option.value = audio.id;
            option.textContent = audio.name;
            this.referenceSelect.appendChild(option);
        });
    }
    
    async onReferenceAudioChange(audioId) {
        this.selectedReferenceId = audioId;
        
        if (!audioId) {
            this.transcriptDisplay.value = '';
            this.referenceContainer.style.display = 'none';
            this.noReferenceMessage.style.display = 'block';
            this.referencePlayer.src = '';
            this.validateForm();
            return;
        }
        
        // Find selected audio
        const selectedAudio = this.referenceAudios.find(audio => audio.id === audioId);
        if (!selectedAudio) {
            safeLogger.error('Selected reference audio not found', audioId);
            return;
        }
        
        safeLogger.info(`Selected reference audio: ${selectedAudio.name}`);
        
        // Update transcript
        this.transcriptDisplay.value = selectedAudio.transcript;
        
        // Show loading state
        this.noReferenceMessage.style.display = 'none';
        this.referenceContainer.style.display = 'block';
        
        // Update reference audio player
        try {
            const audioUrl = `/api/reference-audio/${audioId}/file`;
            this.referencePlayer.src = audioUrl;
            
            // Add loading state
            this.referencePlayer.addEventListener('loadstart', () => {
                safeLogger.info('Loading reference audio preview...');
            });
            
            this.referencePlayer.addEventListener('canplay', () => {
                safeLogger.success('Reference audio preview ready to play');
            });
            
            this.referencePlayer.addEventListener('error', (e) => {
                console.error('Error loading reference audio:', e);
                safeLogger.error('Failed to load reference audio preview');
                this.referenceContainer.style.display = 'none';
                this.noReferenceMessage.style.display = 'block';
            });
            
        } catch (error) {
            console.error('Error setting up reference audio:', error);
            safeLogger.error('Failed to setup reference audio preview', error.message);
        }
        
        this.validateForm();
    }
    
    validateForm() {
        const hasReference = !!this.selectedReferenceId;
        const hasText = this.textInput.value.trim().length > 0;
        
        this.generateBtn.disabled = !hasReference || !hasText || this.isGenerating;
    }
    
    async generateVoice() {
        if (this.isGenerating) return;
        
        const text = this.textInput.value.trim();
        if (!text || !this.selectedReferenceId) {
            safeLogger.error('Please select a reference audio and enter text.');
            return;
        }
        
        this.isGenerating = true;
        this.generateBtn.disabled = true;
        this.loadingSpinner.style.display = 'flex';
        
        safeLogger.info('Starting voice generation...', {
            textLength: text.length,
            referenceId: this.selectedReferenceId
        });
        
        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('text', text);
            formData.append('reference_audio_id', this.selectedReferenceId);
            
            safeLogger.debug('Sending API request to /api/generate-voice');
            
            // Make request to generate voice
            const response = await fetch('/api/generate-voice', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            safeLogger.info('Received audio response, processing...');
            
            // Create blob from response
            const audioBlob = await response.blob();
            safeLogger.debug('Audio blob created', {
                size: audioBlob.size,
                type: audioBlob.type
            });
            
            // Validate audio blob
            if (audioBlob.size === 0) {
                throw new Error('Received empty audio data');
            }
            
            if (audioBlob.size < 100) {
                throw new Error(`Audio data too small: ${audioBlob.size} bytes`);
            }
            
            // Check if it's actually audio data by reading the first few bytes
            const arrayBuffer = await audioBlob.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);
            const header = Array.from(uint8Array.slice(0, 4)).map(b => String.fromCharCode(b)).join('');
            
            safeLogger.debug('Audio header check', {
                header: header,
                headerHex: Array.from(uint8Array.slice(0, 4)).map(b => b.toString(16).padStart(2, '0')).join(' ')
            });
            
            if (header !== 'RIFF') {
                safeLogger.warning('Audio may not be in WAV format', { header });
            }
            
            // Create object URL for audio playback
            const audioUrl = URL.createObjectURL(audioBlob);
            safeLogger.debug('Audio URL created', { url: audioUrl });
            
            // Set up generated audio player with error handling
            this.generatedPlayer.addEventListener('error', (e) => {
                safeLogger.error('Audio playback error', {
                    error: e.error,
                    networkState: this.generatedPlayer.networkState,
                    readyState: this.generatedPlayer.readyState
                });
            }, { once: true });
            
            this.generatedPlayer.addEventListener('loadstart', () => {
                safeLogger.info('Audio loading started');
            }, { once: true });
            
            this.generatedPlayer.addEventListener('canplay', () => {
                safeLogger.success('Audio ready to play');
            }, { once: true });
            
            this.generatedPlayer.addEventListener('loadeddata', () => {
                safeLogger.info('Audio data loaded', {
                    duration: this.generatedPlayer.duration,
                    readyState: this.generatedPlayer.readyState
                });
            }, { once: true });
            
            this.generatedPlayer.src = audioUrl;
            this.generatedSection.style.display = 'block';
            
            // Scroll to generated audio section
            this.generatedSection.scrollIntoView({ behavior: 'smooth' });
            
            safeLogger.success('Voice generated successfully!', {
                audioBlobSize: audioBlob.size,
                audioType: audioBlob.type,
                audioUrl: audioUrl
            });
            
        } catch (error) {
            console.error('Failed to generate voice:', error);
            safeLogger.error(`Failed to generate voice: ${error.message}`);
        } finally {
            this.isGenerating = false;
            this.loadingSpinner.style.display = 'none';
            this.validateForm();
        }
    }
    
    updateAudioProgress() {
        const player = this.generatedPlayer;
        if (!player.duration) return;
        
        const progress = (player.currentTime / player.duration) * 100;
        const progressFill = document.getElementById('progress-fill');
        const currentTimeEl = document.getElementById('current-time');
        const totalTimeEl = document.getElementById('total-time');
        
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(player.currentTime);
        }
        
        if (totalTimeEl) {
            totalTimeEl.textContent = this.formatTime(player.duration);
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit to ensure logger is fully initialized
    setTimeout(() => {
        if (typeof logger !== 'undefined') {
            safeLogger.info('Initializing CosyVoice Web Application...');
            new CosyVoiceApp();
        } else {
            console.error('Logger not available, initializing app without logging');
            new CosyVoiceApp();
        }
    }, 100);
});
