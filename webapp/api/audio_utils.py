"""
Audio utilities for CosyVoice Web Application
"""

import struct

def add_wav_header(raw_audio_data: bytes, sample_rate: int = 22050, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """
    Add WAV header to raw PCM audio data
    
    Args:
        raw_audio_data: Raw PCM audio bytes
        sample_rate: Sample rate in Hz (default: 22050 for CosyVoice)
        channels: Number of audio channels (default: 1 for mono)
        bits_per_sample: Bits per sample (default: 16)
    
    Returns:
        Complete WAV file bytes with header
    """
    
    # Calculate derived values
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(raw_audio_data)
    file_size = 36 + data_size
    
    # Create WAV header
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',           # ChunkID
        file_size,         # ChunkSize
        b'WAVE',           # Format
        b'fmt ',           # Subchunk1ID
        16,                # Subchunk1Size (PCM)
        1,                 # AudioFormat (PCM)
        channels,          # NumChannels
        sample_rate,       # SampleRate
        byte_rate,         # ByteRate
        block_align,       # BlockAlign
        bits_per_sample,   # BitsPerSample
        b'data',           # Subchunk2ID
        data_size          # Subchunk2Size
    )
    
    # Combine header and data
    return wav_header + raw_audio_data

def detect_audio_format(audio_data: bytes) -> dict:
    """
    Detect audio format and properties
    
    Args:
        audio_data: Audio data bytes
        
    Returns:
        Dictionary with format information
    """
    if len(audio_data) < 12:
        return {"format": "unknown", "reason": "too_short"}
    
    # Check for WAV format
    if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
        return {
            "format": "wav",
            "has_header": True,
            "size": len(audio_data)
        }
    
    # Check for other common formats
    if audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
        return {"format": "mp3", "has_header": True}
    
    if audio_data[:4] == b'fLaC':
        return {"format": "flac", "has_header": True}
    
    # Assume raw PCM if no header detected
    return {
        "format": "raw_pcm",
        "has_header": False,
        "size": len(audio_data),
        "estimated_duration_seconds": len(audio_data) / (22050 * 2)  # Assuming 22050Hz, 16-bit
    }
