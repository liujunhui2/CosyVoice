#!/bin/bash

# Initialize conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate cosyvoice environment
conda activate cosyvoice

# Change to webapp directory
cd /home/ubuntu/MyCosyVoice/webapp

# Start the web application
echo "🚀 Starting CosyVoice Web Demo on port 9080..."
python main.py
