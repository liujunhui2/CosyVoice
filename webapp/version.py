"""
Version information for CosyVoice Web Demo
"""

__version__ = "0.1.1"
__title__ = "CosyVoice Web Demo"
__description__ = "Web-based voice cloning application using CosyVoice"
__author__ = "CosyVoice Team"
__license__ = "MIT"

# Version history
VERSION_HISTORY = {
    "0.1.1": {
        "date": "2025-07-01",
        "features": [
            "Simplified audio playback interface",
            "Native browser audio controls integration"
        ],
        "fixes": [
            "Removed custom audio controls in favor of native browser controls",
            "Simplified codebase by removing ~100 lines of custom control logic",
            "Improved accessibility with native audio player",
            "Enhanced user experience consistency across browsers"
        ]
    },
    "0.1.0": {
        "date": "2025-07-01",
        "features": [
            "Basic web interface for voice generation",
            "Reference audio selection and preview",
            "Zero-shot voice cloning with CosyVoice",
            "Real-time logging system",
            "Audio format conversion (raw PCM to WAV)",
            "Comprehensive error handling and debugging",
            "Responsive web design with modern UI"
        ],
        "fixes": [
            "Fixed audio playback issues by adding WAV headers",
            "Resolved logging system display problems",
            "Enhanced error handling for CosyVoice API",
            "Improved audio format detection and validation"
        ]
    }
}
