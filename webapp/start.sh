#!/bin/bash

# CosyVoice Web Application Startup Script

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="9080"
DEFAULT_COSYVOICE_API="http://172.31.26.217:50000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --cosyvoice-api)
            COSYVOICE_API_URL="$2"
            shift 2
            ;;
        --help)
            echo "CosyVoice Web Application Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST                 Host to bind to (default: $DEFAULT_HOST)"
            echo "  --port PORT                 Port to bind to (default: $DEFAULT_PORT)"
            echo "  --cosyvoice-api URL         CosyVoice API URL (default: $DEFAULT_COSYVOICE_API)"
            echo "  --help                      Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  HOST                        Same as --host"
            echo "  PORT                        Same as --port"
            echo "  COSYVOICE_API_URL          Same as --cosyvoice-api"
            echo "  DEBUG                       Enable debug mode (true/false)"
            echo ""
            echo "Examples:"
            echo "  $0                                                    # Use defaults"
            echo "  $0 --port 8080                                       # Custom port"
            echo "  $0 --cosyvoice-api http://192.168.1.100:50000       # Custom API server"
            echo "  DEBUG=true $0                                        # Enable debug mode"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set environment variables with defaults
export HOST="${HOST:-${DEFAULT_HOST}}"
export PORT="${PORT:-${DEFAULT_PORT}}"
export COSYVOICE_API_URL="${COSYVOICE_API_URL:-${DEFAULT_COSYVOICE_API}}"

# Print configuration
echo "========================================="
echo "CosyVoice Web Application"
echo "========================================="
echo "Host:              $HOST"
echo "Port:              $PORT"
echo "CosyVoice API:     $COSYVOICE_API_URL"
echo "Debug:             ${DEBUG:-false}"
echo "========================================="
echo ""

# Check if CosyVoice API is accessible
echo "Checking CosyVoice API connectivity..."
if curl -s --connect-timeout 5 "$COSYVOICE_API_URL/docs" > /dev/null; then
    echo "✅ CosyVoice API is accessible"
else
    echo "❌ Warning: CosyVoice API is not accessible at $COSYVOICE_API_URL"
    echo "   Please check the URL and ensure the service is running"
fi

echo ""
echo "Starting web application..."
echo "Web interface will be available at: http://$HOST:$PORT"
echo ""

# Start the application
cd "$(dirname "$0")"
python3 main.py
