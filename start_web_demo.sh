#!/bin/bash

# CosyVoice Web Demo Startup Script

echo "🎤 Starting CosyVoice Web Demo..."

# Check if we're in the right directory
if [ ! -f "webapp/main.py" ]; then
    echo "❌ Error: Please run this script from the MyCosyVoice root directory"
    exit 1
fi

# Install additional dependencies if needed
echo "📦 Installing additional dependencies..."
pip install aiohttp

# Start the web application
echo "🚀 Starting web application on port 9080..."
echo "📱 Access the demo at: http://localhost:9080"
echo "📚 API documentation at: http://localhost:9080/docs"
echo ""
echo "⚠️  Note: Make sure CosyVoice backend is running on port 50000"
echo "   You can start it with:"
echo "   python runtime/python/fastapi/server.py --port 50000 --model_dir pretrained_models/CosyVoice2-0.5B"
echo ""

cd webapp
python main.py
