# CosyVoice Web Application

A modern web interface for CosyVoice voice cloning technology.

## Features

- **Voice Cloning**: Generate speech using reference audio samples
- **Streaming Audio**: Real-time audio playback without waiting for completion
- **Reference Audio Management**: Select from pre-loaded samples or upload custom audio
- **Responsive Design**: Modern, mobile-friendly interface
- **Configurable Backend**: Easy configuration of CosyVoice API server

## Quick Start

### 1. Basic Usage
```bash
# Start with default settings (CosyVoice API at 172.31.26.217:50000)
./start.sh
```

### 2. Custom Configuration
```bash
# Custom port
./start.sh --port 8080

# Custom CosyVoice API server
./start.sh --cosyvoice-api http://192.168.1.100:50000

# Custom host and port
./start.sh --host 127.0.0.1 --port 3000
```

### 3. Environment Variables
```bash
# Set environment variables
export COSYVOICE_API_URL=http://your-server:50000
export PORT=8080
export DEBUG=true
./start.sh
```

### 4. Using .env File
```bash
# Copy and edit the environment file
cp .env.example .env
# Edit .env with your settings
./start.sh
```

## Configuration Options

### Command Line Arguments
- `--host HOST`: Host to bind to (default: 0.0.0.0)
- `--port PORT`: Port to bind to (default: 9080)
- `--cosyvoice-api URL`: CosyVoice API URL (default: http://172.31.26.217:50000)
- `--help`: Show help message

### Environment Variables
- `HOST`: Server host
- `PORT`: Server port
- `COSYVOICE_API_URL`: CosyVoice API server URL
- `DEBUG`: Enable debug mode (true/false)
- `MAX_AUDIO_FILE_SIZE`: Maximum audio file size in bytes
- `SUPPORTED_AUDIO_FORMATS`: Comma-separated list of supported formats

## API Endpoints

### Web Interface
- `GET /`: Main web interface
- `GET /health`: Health check with CosyVoice connectivity
- `GET /config`: Current configuration

### API Routes
- `GET /api/reference-audios`: List available reference audios
- `GET /api/reference-audio/{id}/file`: Serve reference audio file
- `GET /api/reference-audio/{id}/transcript`: Get audio transcript
- `POST /api/generate-voice`: Generate voice (streaming response)
- `POST /api/upload-reference`: Upload custom reference audio
- `GET /api/health`: API health check

## Architecture

```
User Browser (Port 9080)
    ↓ HTTP Request
FastAPI Web App (Port 9080)
    ↓ Internal API Call
CosyVoice 2.0 Service (Configurable)
    ↓ Audio Stream Response
FastAPI Web App (Port 9080)
    ↓ Streaming Response
User Browser (Audio Playback)
```

## Development

### Manual Start
```bash
cd /home/ubuntu/MyCosyVoice/webapp
python3 main.py
```

### Debug Mode
```bash
DEBUG=true ./start.sh
```

## Troubleshooting

### Check CosyVoice API Connectivity
```bash
curl http://172.31.26.217:50000/docs
```

### View Application Logs
The application logs will show:
- Current configuration
- CosyVoice API connectivity status
- Any errors or warnings

### Common Issues
1. **CosyVoice API not accessible**: Check the URL and ensure the service is running
2. **Port already in use**: Use a different port with `--port` option
3. **Permission denied**: Ensure the script is executable with `chmod +x start.sh`

## Files Structure

```
webapp/
├── main.py                 # Main FastAPI application
├── config.py              # Configuration management
├── start.sh               # Startup script
├── .env                   # Environment configuration
├── .env.example           # Example environment file
├── api/
│   ├── routes.py          # API endpoints
│   └── cosyvoice_client.py # CosyVoice API client
├── static/
│   ├── index.html         # Web interface
│   ├── favicon.svg        # Application icon
│   ├── css/style.css      # Styling
│   └── js/
│       ├── app.js         # Main application logic
│       └── audio.js       # Audio controls
└── README.md              # This file
```
