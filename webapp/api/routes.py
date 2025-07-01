"""
API Routes for CosyVoice Web Application
"""

import os
import json
import time
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse, Response
from pydantic import BaseModel
from .audio_utils import detect_audio_format

from .cosyvoice_client import CosyVoiceClient
from ..config import config

router = APIRouter()

# Initialize CosyVoice client with configuration
cosyvoice_client = CosyVoiceClient()

class ReferenceAudio(BaseModel):
    id: str
    name: str
    file_path: str
    transcript: str
    duration: float

class VoiceGenerationRequest(BaseModel):
    text: str
    reference_audio_id: str

@router.get("/reference-audios", response_model=List[ReferenceAudio])
async def get_reference_audios():
    """Get list of available reference audios"""
    try:
        # For now, return sample reference audios from asset folder
        reference_audios = []
        
        asset_dir = "/home/ubuntu/MyCosyVoice/asset"
        if os.path.exists(asset_dir):
            # Add existing sample audios
            if os.path.exists(f"{asset_dir}/zero_shot_prompt.wav"):
                reference_audios.append(ReferenceAudio(
                    id="zero_shot_prompt",
                    name="Zero Shot Prompt",
                    file_path=f"{asset_dir}/zero_shot_prompt.wav",
                    transcript="希望你以后能够做的比我还好呦。",
                    duration=3.0
                ))
            
            if os.path.exists(f"{asset_dir}/cross_lingual_prompt.wav"):
                reference_audios.append(ReferenceAudio(
                    id="cross_lingual_prompt", 
                    name="Cross Lingual Prompt",
                    file_path=f"{asset_dir}/cross_lingual_prompt.wav",
                    transcript="And then later on, fully acquiring that company.",
                    duration=5.0
                ))
                
            if os.path.exists(f"{asset_dir}/zhouxingchi.wav"):
                # Read transcript from txt file if exists
                transcript = "周星驰经典台词"
                txt_file = f"{asset_dir}/zhouxingchi.txt"
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        transcript = f.read().strip()
                
                reference_audios.append(ReferenceAudio(
                    id="zhouxingchi",
                    name="周星驰",
                    file_path=f"{asset_dir}/zhouxingchi.wav",
                    transcript=transcript,
                    duration=10.0
                ))
        
        return reference_audios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reference audios: {str(e)}")

@router.get("/reference-audio/{audio_id}/file")
async def get_reference_audio_file(audio_id: str):
    """Serve reference audio file for playback"""
    try:
        reference_audios = await get_reference_audios()
        for audio in reference_audios:
            if audio.id == audio_id:
                if os.path.exists(audio.file_path):
                    return FileResponse(
                        audio.file_path,
                        media_type="audio/wav",
                        filename=f"{audio.name}.wav"
                    )
                else:
                    raise HTTPException(status_code=404, detail="Audio file not found")
        
        raise HTTPException(status_code=404, detail="Reference audio not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve audio file: {str(e)}")

@router.get("/reference-audio/{audio_id}/transcript")
async def get_reference_transcript(audio_id: str):
    """Get transcript for a specific reference audio"""
    try:
        reference_audios = await get_reference_audios()
        for audio in reference_audios:
            if audio.id == audio_id:
                return {"transcript": audio.transcript}
        
        raise HTTPException(status_code=404, detail="Reference audio not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")

@router.post("/generate-voice")
async def generate_voice(
    text: str = Form(...),
    reference_audio_id: str = Form(...),
    prompt_text: str = Form(default="")
):
    """Generate voice using CosyVoice backend"""
    try:
        print(f"[API] Generating voice for text: {text[:50]}... with reference: {reference_audio_id}")
        
        # Get reference audio info
        reference_audios = await get_reference_audios()
        reference_audio = None
        for audio in reference_audios:
            if audio.id == reference_audio_id:
                reference_audio = audio
                break
        
        if not reference_audio:
            raise HTTPException(status_code=404, detail="Reference audio not found")
        
        # Use transcript as prompt_text if not provided
        if not prompt_text:
            prompt_text = reference_audio.transcript
        
        print(f"[API] Using prompt text: {prompt_text}")
        print(f"[API] Reference audio path: {reference_audio.file_path}")
        
        # Call CosyVoice backend and get complete audio data
        audio_data = await cosyvoice_client.generate_zero_shot_complete(
            text=text,
            prompt_text=prompt_text,
            prompt_audio_path=reference_audio.file_path
        )
        
        print(f"[API] Generated audio data size: {len(audio_data)} bytes")
        
        # Analyze the audio format
        format_info = detect_audio_format(audio_data)
        print(f"[API] Audio format analysis: {format_info}")
        
        # Save audio to file for debugging (optional)
        import tempfile
        import os
        debug_file = os.path.join(tempfile.gettempdir(), f"debug_audio_{int(time.time())}.wav")
        with open(debug_file, 'wb') as f:
            f.write(audio_data)
        print(f"[API] Debug audio saved to: {debug_file}")
        
        # Verify we have audio data
        if not audio_data or len(audio_data) < 100:  # WAV files should be at least 100 bytes
            raise HTTPException(status_code=500, detail="Generated audio data is too small or empty")
        
        # Verify it's now a proper WAV file
        if format_info["format"] != "wav":
            print(f"[API] Warning: Expected WAV format, got {format_info['format']}")
        else:
            print("[API] Valid WAV file confirmed")
        
        # Return audio data as response
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=generated_voice.wav",
                "Content-Length": str(len(audio_data)),
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error generating voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate voice: {str(e)}")

@router.get("/test-audio")
async def test_audio():
    """Serve a test WAV file to verify audio playback"""
    try:
        # Create a simple test WAV file (1 second of silence at 16kHz)
        import wave
        import tempfile
        import os
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                
                # Generate 1 second of silence
                silence = b'\x00\x00' * 16000  # 16000 samples of 16-bit silence
                wav_file.writeframes(silence)
            
            # Read the file and return it
            with open(tmp_file.name, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(tmp_file.name)
            
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline; filename=test_audio.wav",
                    "Content-Length": str(len(audio_data)),
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "no-cache"
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create test audio: {str(e)}")

@router.get("/health")
async def api_health_check():
    """API health check with CosyVoice connectivity test"""
    try:
        # Test CosyVoice API connectivity
        is_cosyvoice_healthy = await cosyvoice_client.health_check()
        
        return {
            "status": "healthy",
            "cosyvoice_api": {
                "url": config.get_cosyvoice_url(),
                "status": "healthy" if is_cosyvoice_healthy else "unhealthy"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "cosyvoice_api": {
                "url": config.get_cosyvoice_url(),
                "status": "unhealthy",
                "error": str(e)
            }
        }

@router.post("/upload-reference")
async def upload_reference_audio(
    file: UploadFile = File(...),
    name: str = Form(...),
    transcript: str = Form(...)
):
    """Upload custom reference audio"""
    try:
        # Save uploaded file
        upload_dir = "/home/ubuntu/MyCosyVoice/webapp/static/assets/reference_audios"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = f"{upload_dir}/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return reference audio info
        return ReferenceAudio(
            id=file.filename.split('.')[0],
            name=name,
            file_path=file_path,
            transcript=transcript,
            duration=0.0  # TODO: Calculate actual duration
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload reference audio: {str(e)}")
