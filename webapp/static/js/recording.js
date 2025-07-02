/**
 * Recording functionality for CosyVoice Web Demo
 * Handles voice recording, mode switching, and transcription
 */

class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordedBlob = null;
        this.uploadedFile = null; // For file upload functionality
        this.currentMode = 'reference'; // 'reference' or 'recording'
        this.currentReferenceType = 'preset'; // 'preset' or 'user' for reference mode
        this.isLoadingReferences = false; // Flag to prevent unwanted change events
        
        // Voice tag configurations
        this.voiceTags = {
            'Normal': {
                text: '今天我们要聊一个很多人都困惑的话题——如何在忙碌的生活中找到真正属于自己的时间。我最近采访了三位在不同行业工作的朋友，他们都有一个共同点：在极度忙碌的工作中，依然保持着高质量的个人生活。',
                hint: '正常语速的日常语音'
            },
            'Strong': {
                text: '白日依山尽，黄河入海流。欲穷千里目，更上一层楼',
                hint: '朗诵或者强调，慢语速'
            },
            'Soft': {
                text: '最近你经历了很多，压力很大，但这一切都会过去的，给自己一点时间和空间。有时候，我们需要放慢脚步，才能更清楚地看见前方的路。如果累了，就休息一下吧，没人会责怪你。这杯茶还是热的，慢慢喝，让心也跟着平静下来。',
                hint: '轻柔的声音'
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupModeToggle();
        this.setupVoiceTagSelection();
        this.checkMicrophonePermission();
        this.updateUserRecordingList(); // Load existing recordings
    }
    
    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Mode toggle buttons
        const referenceBtn = document.getElementById('reference-mode-btn');
        const recordingBtn = document.getElementById('recording-mode-btn');
        
        console.log('Reference button:', referenceBtn);
        console.log('Recording button:', recordingBtn);
        
        if (referenceBtn) {
            referenceBtn.addEventListener('click', () => {
                console.log('Reference mode clicked');
                this.switchMode('reference');
            });
        } else {
            console.error('Reference mode button not found!');
        }
        
        if (recordingBtn) {
            recordingBtn.addEventListener('click', () => {
                console.log('Recording mode clicked');
                this.switchMode('recording');
            });
        } else {
            console.error('Recording mode button not found!');
        }
        
        // Reference type toggle buttons
        const presetBtn = document.getElementById('preset-audio-btn');
        const userRecordingsBtn = document.getElementById('user-recordings-btn');
        
        if (presetBtn) {
            presetBtn.addEventListener('click', () => {
                this.switchReferenceType('preset');
            });
        }
        
        if (userRecordingsBtn) {
            userRecordingsBtn.addEventListener('click', () => {
                this.switchReferenceType('user');
            });
        }
        
        // Recording controls
        document.getElementById('start-recording-btn').addEventListener('click', () => {
            this.startRecording();
        });
        
        document.getElementById('stop-recording-btn').addEventListener('click', () => {
            this.stopRecording();
        });
        
        document.getElementById('play-recording-btn').addEventListener('click', () => {
            this.playRecording();
        });
        
        // Voice tag selection
        document.getElementById('voice-tag-select').addEventListener('change', (e) => {
            this.updateRecordingText(e.target.value);
        });
        
        // User ID input for filename preview
        document.getElementById('user-id-input').addEventListener('input', () => {
            this.updateFilenamePreview();
            this.updateCommitButtonState();
        });
        
        // Recording text for commit button state
        document.getElementById('recording-text').addEventListener('input', () => {
            this.updateCommitButtonState();
        });
        
        // Transcription
        document.getElementById('transcribe-btn').addEventListener('click', () => {
            this.transcribeAudio();
        });
        
        document.getElementById('use-transcription-btn').addEventListener('click', () => {
            this.useTranscribedText();
        });
        
        // Commit recording
        const commitBtn = document.getElementById('submit-recording-btn');
        if (commitBtn) {
            commitBtn.addEventListener('click', () => {
                this.commitRecording();
            });
            console.log('Commit recording button found and event listener added');
        } else {
            console.error('Commit recording button not found!');
        }
    }
    
    setupModeToggle() {
        // Initialize in reference mode
        this.switchMode('reference');
    }
    
    setupVoiceTagSelection() {
        const select = document.getElementById('voice-tag-select');
        const textArea = document.getElementById('recording-text');
        const hint = document.getElementById('recording-hint');
        
        // Clear and populate options
        select.innerHTML = '<option value="">Select voice tag...</option>';
        Object.keys(this.voiceTags).forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = `${tag} - ${this.voiceTags[tag].hint}`;
            select.appendChild(option);
        });
        
        // Add event listener for voice tag selection
        select.addEventListener('change', () => {
            const selectedTag = select.value;
            if (selectedTag && this.voiceTags[selectedTag]) {
                textArea.value = this.voiceTags[selectedTag].text;
                if (hint) {
                    hint.textContent = this.voiceTags[selectedTag].hint;
                }
            } else {
                textArea.value = '';
                if (hint) {
                    hint.textContent = '';
                }
            }
            this.updateFilenamePreview();
            this.updateCommitButtonState();
        });
    }
    
    switchMode(mode) {
        console.log('Switching to mode:', mode);
        this.currentMode = mode;
        
        // Update button states
        const referenceBtn = document.getElementById('reference-mode-btn');
        const recordingBtn = document.getElementById('recording-mode-btn');
        
        console.log('Found buttons - Reference:', !!referenceBtn, 'Recording:', !!recordingBtn);
        
        if (mode === 'reference') {
            console.log('Switching to reference mode');
            if (referenceBtn) referenceBtn.classList.add('active');
            if (recordingBtn) recordingBtn.classList.remove('active');
            
            // Show/hide sections
            const refSection = document.getElementById('reference-section');
            const recSection = document.getElementById('recording-section');
            const refInstructions = document.getElementById('reference-mode-instructions');
            const recInstructions = document.getElementById('recording-mode-instructions');
            const voiceGenContent = document.getElementById('voice-generation-content');
            
            console.log('Found sections - Ref:', !!refSection, 'Rec:', !!recSection);
            
            if (refSection) refSection.style.display = 'block';
            if (recSection) recSection.style.display = 'none';
            if (refInstructions) refInstructions.style.display = 'block';
            if (recInstructions) recInstructions.style.display = 'none';
            if (voiceGenContent) voiceGenContent.style.display = 'block';
            
            // Show user recording section if recordings exist
            this.updateUserRecordingVisibility();
            
            // Initialize reference type toggle to preset
            this.switchReferenceType('preset');
            
        } else {
            recordingBtn.classList.add('active');
            referenceBtn.classList.remove('active');
            
            // Show/hide sections
            document.getElementById('reference-section').style.display = 'none';
            document.getElementById('recording-section').style.display = 'block';
            document.getElementById('reference-mode-instructions').style.display = 'none';
            document.getElementById('recording-mode-instructions').style.display = 'block';
            
            // Hide voice generation content in recording mode
            document.getElementById('voice-generation-content').style.display = 'none';
        }
        
        // Update generation button state
        this.updateGenerateButtonState();
        
        // Log mode switch
        if (window.logger) {
            window.logger.info(`Switched to ${mode} mode`);
        }
    }
    
    updateRecordingText(tag) {
        const textArea = document.getElementById('recording-text');
        const hint = document.getElementById('recording-hint');
        const startBtn = document.getElementById('start-recording-btn');
        
        if (tag && this.voiceTags[tag]) {
            textArea.value = this.voiceTags[tag].text;
            hint.textContent = `💡 ${this.voiceTags[tag].hint}`;
            startBtn.disabled = false;
        } else {
            textArea.value = '';
            hint.textContent = 'Select a voice tag above to see the recording hint.';
            startBtn.disabled = true;
        }
        
        // Update filename preview
        this.updateFilenamePreview();
    }
    
    updateFilenamePreview() {
        const userId = document.getElementById('user-id-input').value.trim();
        const voiceTag = document.getElementById('voice-tag-select').value;
        
        const filenamePreview = document.getElementById('filename-preview');
        const textfilePreview = document.getElementById('textfile-preview');
        const filenameHint = document.getElementById('filename-hint');
        
        if (userId && voiceTag) {
            const audioFilename = `${userId}_${voiceTag}.wav`;
            const textFilename = `${userId}_${voiceTag}.txt`;
            
            if (filenamePreview) filenamePreview.textContent = audioFilename;
            if (textfilePreview) textfilePreview.textContent = textFilename;
            if (filenameHint) filenameHint.textContent = audioFilename;
        } else {
            if (filenamePreview) filenamePreview.textContent = '请输入用户ID和选择标签';
            if (textfilePreview) textfilePreview.textContent = '请输入用户ID和选择标签';
            if (filenameHint) filenameHint.textContent = '请输入用户ID和选择标签';
        }
    }
    
    updateUserRecordingVisibility() {
        // This function is no longer needed since user recordings are now handled
        // through the unified reference selection with toggle buttons
        // Keeping empty function to avoid breaking existing calls
    }
    
    switchReferenceType(type) {
        console.log('Switching reference type to:', type);
        this.currentReferenceType = type;
        
        // Update button states
        const presetBtn = document.getElementById('preset-audio-btn');
        const userBtn = document.getElementById('user-recordings-btn');
        const label = document.getElementById('reference-select-label');
        const transcriptDisplay = document.getElementById('transcript-display');
        
        // Clear transcript and reset to placeholder state when switching
        if (transcriptDisplay) {
            transcriptDisplay.value = '';
            transcriptDisplay.placeholder = type === 'preset' 
                ? 'Select a preset audio to see its transcript'
                : 'Select your recording to see its transcript';
        }
        
        if (type === 'preset') {
            if (presetBtn) presetBtn.classList.add('active');
            if (userBtn) userBtn.classList.remove('active');
            if (label) label.textContent = 'Choose Preset Audio:';
            this.loadPresetAudio();
        } else {
            if (presetBtn) presetBtn.classList.remove('active');
            if (userBtn) userBtn.classList.add('active');
            if (label) label.textContent = 'Choose Your Recording:';
            this.loadUserRecordingsForReference();
        }
    }
    
    async loadPresetAudio() {
        // Load the original preset audio files
        try {
            this.isLoadingReferences = true;
            
            const response = await fetch('/api/reference-audios');
            const audios = await response.json();
            
            const select = document.getElementById('reference-select');
            select.innerHTML = '<option value="">Select preset audio...</option>';
            
            audios.forEach(audio => {
                const option = document.createElement('option');
                option.value = audio.id;
                option.textContent = audio.name;
                option.dataset.transcript = audio.transcript;
                select.appendChild(option);
            });
            
            if (window.logger) {
                window.logger.success(`Loaded ${audios.length} preset audio files`);
            }
            
        } catch (error) {
            console.error('Failed to load preset audio:', error);
            if (window.logger) {
                window.logger.error('Failed to load preset audio: ' + error.message);
            }
        } finally {
            this.isLoadingReferences = false;
        }
    }
    
    async loadUserRecordingsForReference() {
        try {
            this.isLoadingReferences = true;
            
            const response = await fetch('/api/user-recordings');
            const recordings = await response.json();
            
            const select = document.getElementById('reference-select');
            select.innerHTML = '<option value="">Select your recording...</option>';
            
            // Group recordings by user ID
            const groupedRecordings = {};
            recordings.forEach(recording => {
                if (!groupedRecordings[recording.user_id]) {
                    groupedRecordings[recording.user_id] = [];
                }
                groupedRecordings[recording.user_id].push(recording);
            });
            
            // Add grouped options
            Object.keys(groupedRecordings).forEach(userId => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = `User: ${userId}`;
                
                groupedRecordings[userId].forEach(recording => {
                    const option = document.createElement('option');
                    option.value = `user_recording:${recording.id}`;
                    option.textContent = `${recording.voice_tag}`;
                    option.dataset.transcript = recording.text;
                    optgroup.appendChild(option);
                });
                
                select.appendChild(optgroup);
            });
            
            if (recordings.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No recordings found - record some audio first!';
                option.disabled = true;
                select.appendChild(option);
            }
            
            console.log(`Loaded ${recordings.length} user recordings for reference selection`);
            
        } catch (error) {
            console.error('Failed to load user recordings:', error);
            if (window.logger) {
                window.logger.error('Failed to load user recordings: ' + error.message);
            }
        } finally {
            this.isLoadingReferences = false;
        }
    }
    
    async checkMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            
            if (window.logger) {
                window.logger.success('Microphone access granted');
            }
        } catch (error) {
            if (window.logger) {
                window.logger.error('Microphone access denied or not available');
            }
            
            // Disable recording functionality
            document.getElementById('start-recording-btn').disabled = true;
            document.getElementById('recording-status').innerHTML = 
                '<span style="color: #d32f2f;">❌ Microphone access required for recording</span>';
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.recordedBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.showRecordedAudio();
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.updateRecordingUI();
            
            if (window.logger) {
                window.logger.info('Recording started');
            }
            
        } catch (error) {
            if (window.logger) {
                window.logger.error('Failed to start recording: ' + error.message);
            }
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI();
            
            if (window.logger) {
                window.logger.info('Recording stopped');
            }
        }
    }
    
    updateRecordingUI() {
        const startBtn = document.getElementById('start-recording-btn');
        const stopBtn = document.getElementById('stop-recording-btn');
        const playBtn = document.getElementById('play-recording-btn');
        const status = document.getElementById('recording-status');
        
        if (this.isRecording) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            playBtn.disabled = true;
            status.innerHTML = '<span class="recording-status recording">🔴 Recording in progress...</span>';
        } else if (this.recordedBlob) {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            playBtn.disabled = false;
            status.innerHTML = '<span class="recording-status ready">✅ Recording complete</span>';
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            playBtn.disabled = true;
            status.innerHTML = '<span class="recording-status stopped">⏹️ Ready to record</span>';
        }
    }
    
    showRecordedAudio() {
        console.log('showRecordedAudio called, recordedBlob:', !!this.recordedBlob);
        const section = document.getElementById('recorded-audio-section');
        const player = document.getElementById('recorded-player');
        const submitSection = document.getElementById('submit-recording-section');
        
        console.log('Found elements - section:', !!section, 'player:', !!player, 'submitSection:', !!submitSection);
        
        if (this.recordedBlob) {
            const audioUrl = URL.createObjectURL(this.recordedBlob);
            player.src = audioUrl;
            section.style.display = 'block';
            
            // Always show the recording options
            player.onloadedmetadata = () => {
                console.log('Audio loaded, duration:', player.duration, 'seconds');
                
                // Always show both sections - no duration checking
                this.showRecordingOptions();
            };
            
            // Force load the audio
            player.load();
            
        }
    }
    
    showRecordingOptions() {
        const submitSection = document.getElementById('submit-recording-section');
        const transcriptionSection = document.getElementById('transcription-section');
        
        // Always show both sections
        transcriptionSection.style.display = 'block';
        submitSection.style.display = 'block';
        
        // Update commit button state based on form fields
        this.updateCommitButtonState();
        
        if (window.logger) {
            window.logger.success('Recording ready! You can now transcribe or commit the recording.');
        }
    }
    
    updateCommitButtonState() {
        const userId = document.getElementById('user-id-input').value.trim();
        const voiceTag = document.getElementById('voice-tag-select').value;
        const recordingText = document.getElementById('recording-text').value.trim();
        const commitBtn = document.getElementById('submit-recording-btn');
        
        // Enable commit button only if all required fields are filled and we have a recording
        const canCommit = userId && voiceTag && recordingText && this.recordedBlob;
        commitBtn.disabled = !canCommit;
        
        // Always show normal button text
        commitBtn.textContent = '💾 Commit Recording';
        
        if (canCommit) {
            commitBtn.classList.remove('btn-secondary');
            commitBtn.classList.add('btn-success');
        } else {
            commitBtn.classList.remove('btn-success');
            commitBtn.classList.add('btn-secondary');
        }
    }
    
    playRecording() {
        const player = document.getElementById('recorded-player');
        if (player.src) {
            player.play();
        }
    }
    
    async transcribeAudio() {
        if (!this.recordedBlob) {
            if (window.logger) {
                window.logger.error('No audio recording available for transcription');
            }
            return;
        }
        
        const transcribeBtn = document.getElementById('transcribe-btn');
        const loading = document.getElementById('transcribe-loading');
        const resultSection = document.getElementById('transcription-result');
        
        try {
            // Show loading
            transcribeBtn.disabled = true;
            loading.style.display = 'flex';
            
            if (window.logger) {
                window.logger.info('Starting transcription...');
            }
            
            // Create FormData for audio upload
            const formData = new FormData();
            formData.append('audio', this.recordedBlob, 'recording.webm');
            
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Transcription failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Display transcription result
            document.getElementById('transcribed-text').value = result.transcript;
            resultSection.style.display = 'block';
            
            if (window.logger) {
                window.logger.success('Transcription completed');
            }
            
        } catch (error) {
            if (window.logger) {
                window.logger.error('Transcription failed: ' + error.message);
            }
        } finally {
            // Hide loading
            transcribeBtn.disabled = false;
            loading.style.display = 'none';
        }
    }
    
    useTranscribedText() {
        const transcribedText = document.getElementById('transcribed-text').value;
        const recordingText = document.getElementById('recording-text');
        
        if (transcribedText.trim()) {
            recordingText.value = transcribedText;
            
            if (window.logger) {
                window.logger.info('Used transcribed text for recording');
            }
        }
    }
    
    async commitRecording() {
        const userId = document.getElementById('user-id-input').value.trim();
        const voiceTag = document.getElementById('voice-tag-select').value;
        const recordingText = document.getElementById('recording-text').value.trim();
        
        if (!userId || !voiceTag || !recordingText || !this.recordedBlob) {
            if (window.logger) {
                window.logger.error('Please complete all fields and record audio before committing');
            }
            return;
        }
        
        try {
            if (window.logger) {
                window.logger.info('Committing recording to backend...');
            }
            
            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('voice_tag', voiceTag);
            formData.append('text', recordingText);
            formData.append('audio', this.recordedBlob, `${userId}_${voiceTag}.wav`);
            
            const response = await fetch('/api/commit-recording', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Commit failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (window.logger) {
                window.logger.success(`Recording committed successfully! Saved as ${result.audio_file} and ${result.text_file}`);
            }
            
            // Update user recording selection in generation section
            await this.updateUserRecordingList();
            
            // Clear form but keep user ID
            this.resetRecordingFormKeepUserId();
            
        } catch (error) {
            if (window.logger) {
                window.logger.error('Failed to commit recording: ' + error.message);
            }
        }
    }
    
    resetRecordingForm() {
        // Reset form fields
        document.getElementById('user-id-input').value = '';
        document.getElementById('voice-tag-select').value = '';
        document.getElementById('recording-text').value = '';
        
        // Reset recording state
        this.recordedBlob = null;
        this.isRecording = false;
        
        // Hide sections
        document.getElementById('recorded-audio-section').style.display = 'none';
        document.getElementById('transcription-section').style.display = 'none';
        document.getElementById('submit-recording-section').style.display = 'none';
        
        // Update UI
        this.updateRecordingUI();
        this.updateFilenamePreview();
        
        if (window.logger) {
            window.logger.info('Recording form reset for next upload');
        }
    }
    
    resetRecordingFormKeepUserId() {
        // Keep user ID, reset other form fields
        const userId = document.getElementById('user-id-input').value; // Save current user ID
        document.getElementById('voice-tag-select').value = '';
        document.getElementById('recording-text').value = '';
        
        // Reset recording state
        this.recordedBlob = null;
        this.isRecording = false;
        
        // Hide sections
        document.getElementById('recorded-audio-section').style.display = 'none';
        document.getElementById('transcription-section').style.display = 'none';
        document.getElementById('submit-recording-section').style.display = 'none';
        
        // Update UI
        this.updateRecordingUI();
        this.updateFilenamePreview();
        
        // Restore user ID
        document.getElementById('user-id-input').value = userId;
        
        if (window.logger) {
            window.logger.info('Recording form reset, user ID preserved for next recording');
        }
    }
    
    async updateUserRecordingList() {
        // This function is no longer needed since user recordings are now handled
        // through the unified reference selection with toggle buttons
        // Keeping empty function to avoid breaking existing calls
    }
    
    updateGenerateButtonState() {
        const generateBtn = document.getElementById('generate-btn');
        const textInput = document.getElementById('text-input');
        
        if (this.currentMode === 'reference') {
            // Reference mode: need reference audio selected
            const referenceSelect = document.getElementById('reference-select');
            generateBtn.disabled = !referenceSelect.value || !textInput.value.trim();
        } else {
            // Recording mode: voice generation is disabled
            generateBtn.disabled = true;
        }
    }
}

// Initialize recorder when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing VoiceRecorder');
    try {
        window.voiceRecorder = new VoiceRecorder();
        console.log('VoiceRecorder initialized successfully');
    } catch (error) {
        console.error('Error initializing VoiceRecorder:', error);
    }
});
