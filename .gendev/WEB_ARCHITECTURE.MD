# Web Application Architecture Scaffold

## Port Configuration
- **Port 9080**: Main web application (Frontend + API Gateway)
- **172.31.26.217:50000**: CosyVoice 2.0 FastAPI backend service (External)

## Application Structure

### Frontend (Port 9080)
**Technology**: FastAPI serving static files + REST API endpoints
**Location**: `/home/ubuntu/MyCosyVoice/webapp/`

```
webapp/
├── main.py                 # Main FastAPI application (Port 9080)
├── static/                 # Static web files
│   ├── index.html         # Main web interface
│   ├── css/
│   │   └── style.css      # Styling
│   ├── js/
│   │   ├── app.js         # Main application logic
│   │   └── audio.js       # Audio streaming/control logic
│   └── assets/
│       └── reference_audios/  # Sample reference audio files
├── templates/             # HTML templates (if needed)
└── api/
    ├── __init__.py
    ├── routes.py          # API endpoints for frontend
    └── cosyvoice_client.py # Client to communicate with port 50000
```

### Backend Service (172.31.26.217:50000)
**Technology**: CosyVoice 2.0 FastAPI service
**Location**: External server at 172.31.26.217:50000

## Data Flow

```
User Browser (Port 9080)
    ↓ HTTP Request
FastAPI Web App (Port 9080)
    ↓ Internal API Call
CosyVoice 2.0 Service (172.31.26.217:50000)
    ↓ Audio Stream Response
FastAPI Web App (Port 9080)
    ↓ Streaming Response
User Browser (Audio Playback)
```

## API Endpoints (Port 9080)

### Frontend Routes
- `GET /` - Main web interface
- `GET /static/*` - Static files (CSS, JS, assets)
- `GET /health` - Health check

### API Routes
- `GET /api/reference-audios` - List available reference audios
- `POST /api/generate-voice` - Generate voice with streaming response
- `GET /api/reference-audio/{id}/transcript` - Get transcript for reference audio
- `POST /api/upload-reference` - Upload custom reference audio

## Access URLs
- **Web Interface**: http://localhost:9080
- **API Documentation**: http://localhost:9080/docs
- **Health Check**: http://localhost:9080/health
