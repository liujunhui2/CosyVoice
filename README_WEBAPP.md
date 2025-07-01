# CosyVoice Web Demo v0.1.0

A modern web-based voice cloning application built on top of CosyVoice, providing an intuitive interface for zero-shot voice generation.

## 🌟 Features

### Core Functionality
- **Zero-Shot Voice Cloning**: Generate speech in any voice using just a reference audio sample
- **Web-Based Interface**: Modern, responsive web application
- **Real-Time Audio Preview**: Listen to reference audio and generated results
- **Multiple Reference Voices**: Pre-loaded reference audio samples
- **Live Logging**: Real-time logging system with multiple log levels

### Technical Features
- **Audio Format Conversion**: Automatic conversion of raw PCM to browser-compatible WAV
- **Comprehensive Error Handling**: Detailed error messages and debugging information
- **Async Processing**: Non-blocking audio generation with progress indicators
- **Format Detection**: Automatic audio format detection and validation
- **Debug Tools**: Built-in audio testing and format validation

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- CosyVoice backend running (see main README.md)
- Modern web browser with audio support

### Installation
```bash
# Install dependencies
pip install -r webapp/requirements.txt

# Start the web application
cd webapp
python main.py
```

### Usage
1. Open http://localhost:9080 in your browser
2. Select a reference audio from the dropdown
3. Enter the text you want to generate
4. Click "Generate Voice" and wait for the result
5. Play the generated audio using the built-in player

## 🏗️ Architecture

### Backend (FastAPI)
- **API Routes**: RESTful endpoints for audio generation and management
- **CosyVoice Client**: Async client for backend communication
- **Audio Processing**: WAV header generation and format conversion
- **Error Handling**: Comprehensive exception handling and logging

### Frontend (Vanilla JavaScript)
- **Modern ES6+**: Clean, maintainable JavaScript code
- **Responsive Design**: Mobile-friendly interface
- **Real-Time Logging**: Console-style logging with timestamps
- **Audio Controls**: Custom audio player with advanced controls

### Audio Pipeline
```
Text Input → CosyVoice API → Raw PCM → WAV Conversion → Browser Playback
```

## 📁 Project Structure

```
webapp/
├── api/                    # Backend API
│   ├── routes.py          # API endpoints
│   ├── cosyvoice_client.py # CosyVoice integration
│   ├── audio_utils.py     # Audio processing utilities
│   └── models.py          # Data models
├── static/                # Frontend assets
│   ├── css/style.css      # Styling
│   ├── js/                # JavaScript modules
│   │   ├── app.js         # Main application logic
│   │   ├── audio.js       # Audio controls
│   │   └── logger.js      # Logging system
│   └── index.html         # Main interface
├── reference_audios/      # Sample audio files
├── config.py             # Configuration
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables
- `COSYVOICE_API_URL`: CosyVoice backend URL (default: http://172.31.26.217:50000)
- `WEB_PORT`: Web application port (default: 9080)
- `DEBUG`: Enable debug mode (default: False)

### Audio Settings
- **Sample Rate**: 22050 Hz (CosyVoice standard)
- **Channels**: Mono (1 channel)
- **Bit Depth**: 16-bit PCM
- **Format**: WAV with proper headers

## 🐛 Debugging

### Built-in Debug Tools
- **🧪 Test Log**: Test the logging system functionality
- **🔊 Test Audio**: Test basic audio playback with known good file
- **Debug Files**: Generated audio saved to `/tmp/debug_audio_*.wav`

### Common Issues
1. **Audio Won't Play**: Check browser console for errors, try test audio button
2. **No Reference Audio**: Ensure reference audio files are in `reference_audios/` directory
3. **Backend Connection**: Verify CosyVoice backend is running and accessible

### Log Levels
- **INFO**: General information and status updates
- **SUCCESS**: Successful operations and completions
- **WARNING**: Non-critical issues and warnings
- **ERROR**: Errors and failures
- **DEBUG**: Detailed debugging information

## 🔄 Version History

### v0.1.0 (2025-07-01)
- Initial release with core voice cloning functionality
- Web interface with reference audio selection
- Audio format conversion and playback
- Real-time logging system
- Comprehensive error handling

## 🤝 Contributing

This is part of the larger CosyVoice project. See the main repository for contribution guidelines.

## 📄 License

This project follows the same license as the main CosyVoice project.

## 🙏 Acknowledgments

Built on top of the excellent [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) project by the FunAudioLLM team.
