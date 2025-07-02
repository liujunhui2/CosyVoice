# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-07-02

### Added
- Simplified commit button logic - always visible and functional
- Streamlined recording workflow for better user experience
- Enhanced user experience with consistent button behavior

### Fixed
- Fixed 'Recording too long (Infinitys)' error message bug
- Removed unreliable WebM duration detection from frontend
- Simplified JavaScript codebase by removing ~200 lines of duration handling
- Eliminated confusing button state changes during recording
- Improved recording UI consistency and reliability

### Removed
- Complex frontend duration validation (moved to backend for future implementation)
- Duration-based button state management
- Frontend audio duration checking logic

## [0.2.0] - 2025-07-02

### Added
- Voice recording duration validation (30-second limit)
- Enhanced error handling for long recordings
- Improved recording status feedback
- Added duration-based commit button states

### Fixed
- Added recording length validation to prevent backend timeouts
- Fixed TransferEncodingError with long reference audio files
- Enhanced user feedback for recording duration limits
- Improved audio file processing reliability

## [0.1.1] - 2025-07-01

### Added
- Simplified audio playbook interface
- Native browser audio controls integration

### Fixed
- Removed custom audio controls in favor of native browser controls
- Simplified codebase by removing ~100 lines of custom control logic
- Improved accessibility with native audio player
- Enhanced user experience consistency across browsers

## [0.1.0] - 2025-07-01

### Added
- Basic web interface for voice generation
- Reference audio selection and preview
- Zero-shot voice cloning with CosyVoice
- Real-time logging system
- Audio format conversion (raw PCM to WAV)
- Comprehensive error handling and debugging
- Responsive web design with modern UI

### Fixed
- Fixed audio playbook issues by adding WAV headers
- Resolved logging system display problems
- Enhanced error handling for CosyVoice API
- Improved audio format detection and validation
