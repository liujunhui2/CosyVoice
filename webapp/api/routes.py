"""
API Routes for CosyVoice Web Application
"""

import os
import json
import time
import subprocess
import tempfile
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse, Response
from pydantic import BaseModel
from .audio_utils import detect_audio_format

from .cosyvoice_client import CosyVoiceClient
from .aws_transcribe import transcribe_service
from ..config import config

router = APIRouter()

# Initialize CosyVoice client with configuration
cosyvoice_client = CosyVoiceClient()

def convert_webm_to_wav(input_path: str, output_path: str) -> bool:
    """
    Convert WebM audio file to WAV format using FFmpeg
    Returns True if successful, False otherwise
    """
    try:
        # FFmpeg command to convert WebM to WAV with specific parameters for CosyVoice
        cmd = [
            'ffmpeg',
            '-i', input_path,           # Input file
            '-f', 'wav',                # Output format WAV
            '-acodec', 'pcm_s16le',     # PCM 16-bit little-endian codec
            '-ar', '16000',             # Sample rate 16kHz (common for speech)
            '-ac', '1',                 # Mono channel
            '-y',                       # Overwrite output file
            output_path                 # Output file
        ]
        
        # Run FFmpeg conversion
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[CONVERT] Successfully converted {input_path} to {output_path}")
            return True
        else:
            print(f"[CONVERT] FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[CONVERT] Exception during conversion: {str(e)}")
        return False

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
    mode: str = Form(default="reference"),
    prompt_text: str = Form(default="")
):
    """Generate voice using CosyVoice backend"""
    try:
        print(f"[API] Generating voice for text: {text[:50]}... with reference: {reference_audio_id} in {mode} mode")
        
        reference_audio_path = None
        
        if mode == "recording" or mode == "user_recording":
            # Handle user recording mode
            user_recordings = await get_user_recordings()
            print(f"[API] Available user recordings: {[r.id for r in user_recordings]}")
            print(f"[API] Looking for recording ID: {reference_audio_id}")
            
            user_recording = None
            for recording in user_recordings:
                if recording.id == reference_audio_id:
                    user_recording = recording
                    break
            
            if not user_recording:
                print(f"[API] ERROR: User recording not found. Available IDs: {[r.id for r in user_recordings]}")
                raise HTTPException(status_code=404, detail="Reference audio not found")
            
            reference_audio_path = user_recording.file_path
            if not prompt_text:
                prompt_text = user_recording.text
            
            print(f"[API] Using user recording: {user_recording.user_id} - {user_recording.voice_tag}")
            
        else:
            # Handle reference audio mode
            reference_audios = await get_reference_audios()
            reference_audio = None
            for audio in reference_audios:
                if audio.id == reference_audio_id:
                    reference_audio = audio
                    break
            
            if not reference_audio:
                raise HTTPException(status_code=404, detail="Reference audio not found")
            
            reference_audio_path = reference_audio.file_path
            if not prompt_text:
                prompt_text = reference_audio.transcript
        
        print(f"[API] Using prompt text: {prompt_text}")
        print(f"[API] Reference audio path: {reference_audio_path}")
        
        # Call CosyVoice backend and get complete audio data
        audio_data = await cosyvoice_client.generate_zero_shot_complete(
            text=text,
            prompt_text=prompt_text,
            prompt_audio_path=reference_audio_path
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

# Recording and Transcription Endpoints

class UserRecording(BaseModel):
    id: str
    user_id: str
    voice_tag: str
    text: str
    file_path: str
    transcript: str = ""
    created_at: str

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe uploaded audio using AWS Transcribe"""
    try:
        # Save uploaded audio temporarily
        temp_dir = "/tmp/cosyvoice_transcribe"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = f"{temp_dir}/{int(time.time())}_{audio.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Use AWS Transcribe service
        transcript = await transcribe_service.transcribe_audio(temp_file_path, 'zh-CN')
        
        # Clean up temp file
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return {"transcript": transcript}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/commit-recording")
async def commit_recording(
    user_id: str = Form(...),
    voice_tag: str = Form(...),
    text: str = Form(...),
    audio: UploadFile = File(...)
):
    """Commit a user recording to asset/recorded folder"""
    try:
        # Create recordings directory in asset/recorded
        recordings_dir = "/home/ubuntu/MyCosyVoice/asset/recorded"
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Generate filename using userid_tag convention
        audio_filename = f"{user_id}_{voice_tag}.wav"
        text_filename = f"{user_id}_{voice_tag}.txt"
        
        audio_file_path = f"{recordings_dir}/{audio_filename}"
        text_file_path = f"{recordings_dir}/{text_filename}"
        
        # Save audio file with conversion
        temp_audio_path = None
        try:
            # First save the uploaded file to a temporary location
            temp_audio_path = f"{audio_file_path}.temp"
            with open(temp_audio_path, "wb") as buffer:
                content = await audio.read()
                buffer.write(content)
            
            # Check if the file is WebM and needs conversion
            file_type = subprocess.run(['file', temp_audio_path], capture_output=True, text=True)
            if 'WebM' in file_type.stdout or 'webm' in file_type.stdout:
                print(f"[RECORDING] Detected WebM format, converting to WAV...")
                # Convert WebM to WAV
                if convert_webm_to_wav(temp_audio_path, audio_file_path):
                    print(f"[RECORDING] Successfully converted to WAV format")
                else:
                    raise HTTPException(status_code=500, detail="Failed to convert audio format")
            else:
                # File is already in correct format, just move it
                os.rename(temp_audio_path, audio_file_path)
                print(f"[RECORDING] Audio file saved without conversion")
                
        finally:
            # Clean up temporary file if it exists
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        
        # Save text file
        with open(text_file_path, "w", encoding='utf-8') as f:
            f.write(text)
        
        # Create recording metadata
        timestamp = int(time.time())
        recording = UserRecording(
            id=f"{user_id}_{voice_tag}",
            user_id=user_id,
            voice_tag=voice_tag,
            text=text,
            file_path=audio_file_path,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save metadata to JSON file in asset/recorded
        metadata_file = f"{recordings_dir}/recordings_metadata.json"
        recordings_data = []
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                recordings_data = json.load(f)
        
        # Remove existing recording with same user_id and voice_tag
        recordings_data = [r for r in recordings_data if not (r['user_id'] == user_id and r['voice_tag'] == voice_tag)]
        
        # Add new recording
        recordings_data.append(recording.dict())
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(recordings_data, f, ensure_ascii=False, indent=2)
        
        return {
            "message": "Recording committed successfully", 
            "recording_id": recording.id,
            "audio_file": audio_filename,
            "text_file": text_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to commit recording: {str(e)}")

@router.post("/submit-recording")
async def submit_recording(
    user_id: str = Form(...),
    voice_tag: str = Form(...),
    text: str = Form(...),
    audio: UploadFile = File(...)
):
    """Submit a user recording"""
    try:
        # Create recordings directory
        recordings_dir = "/home/ubuntu/MyCosyVoice/webapp/static/assets/user_recordings"
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Generate filename using userid_tag convention
        audio_filename = f"{user_id}_{voice_tag}.wav"
        text_filename = f"{user_id}_{voice_tag}.txt"
        
        audio_file_path = f"{recordings_dir}/{audio_filename}"
        text_file_path = f"{recordings_dir}/{text_filename}"
        
        # Save audio file
        with open(audio_file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Save text file
        with open(text_file_path, "w", encoding='utf-8') as f:
            f.write(text)
        
        # Create recording metadata
        timestamp = int(time.time())
        recording = UserRecording(
            id=f"{user_id}_{voice_tag}",
            user_id=user_id,
            voice_tag=voice_tag,
            text=text,
            file_path=audio_file_path,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save metadata to JSON file
        metadata_file = f"{recordings_dir}/recordings_metadata.json"
        recordings_data = []
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                recordings_data = json.load(f)
        
        # Remove existing recording with same user_id and voice_tag
        recordings_data = [r for r in recordings_data if not (r['user_id'] == user_id and r['voice_tag'] == voice_tag)]
        
        # Add new recording
        recordings_data.append(recording.dict())
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(recordings_data, f, ensure_ascii=False, indent=2)
        
        return {
            "message": "Recording uploaded successfully", 
            "recording_id": recording.id,
            "audio_file": audio_filename,
            "text_file": text_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit recording: {str(e)}")

@router.get("/user-recordings", response_model=List[UserRecording])
async def get_user_recordings():
    """Get list of user recordings from asset/recorded folder"""
    try:
        # Check asset/recorded folder first (new location)
        recordings_dir = "/home/ubuntu/MyCosyVoice/asset/recorded"
        metadata_file = f"{recordings_dir}/recordings_metadata.json"
        
        recordings_data = []
        
        # Load from asset/recorded if exists
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                recordings_data.extend(json.load(f))
        
        # Also check old location for backward compatibility
        old_recordings_dir = "/home/ubuntu/MyCosyVoice/webapp/static/assets/user_recordings"
        old_metadata_file = f"{old_recordings_dir}/recordings_metadata.json"
        
        if os.path.exists(old_metadata_file):
            with open(old_metadata_file, 'r', encoding='utf-8') as f:
                old_recordings = json.load(f)
                # Add old recordings that don't exist in new location
                existing_ids = {r['id'] for r in recordings_data}
                for old_rec in old_recordings:
                    if old_rec['id'] not in existing_ids:
                        recordings_data.append(old_rec)
        
        return [UserRecording(**recording) for recording in recordings_data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load user recordings: {str(e)}")

@router.get("/user-recording/{recording_id}")
async def get_user_recording_file(recording_id: str):
    """Serve user recording audio file from asset/recorded or old location"""
    try:
        # Check asset/recorded folder first (new location)
        recordings_dir = "/home/ubuntu/MyCosyVoice/asset/recorded"
        metadata_file = f"{recordings_dir}/recordings_metadata.json"
        
        recording = None
        
        # Look in new location first
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                recordings_data = json.load(f)
                for rec in recordings_data:
                    if rec['id'] == recording_id:
                        recording = rec
                        break
        
        # If not found, check old location
        if not recording:
            old_recordings_dir = "/home/ubuntu/MyCosyVoice/webapp/static/assets/user_recordings"
            old_metadata_file = f"{old_recordings_dir}/recordings_metadata.json"
            
            if os.path.exists(old_metadata_file):
                with open(old_metadata_file, 'r', encoding='utf-8') as f:
                    recordings_data = json.load(f)
                    for rec in recordings_data:
                        if rec['id'] == recording_id:
                            recording = rec
                            break
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        if not os.path.exists(recording['file_path']):
            raise HTTPException(status_code=404, detail="Recording file not found")
        
        return FileResponse(
            recording['file_path'],
            media_type="audio/wav",
            filename=f"{recording['user_id']}_{recording['voice_tag']}.wav"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve recording: {str(e)}")
