"""
Client for communicating with CosyVoice FastAPI backend
"""

import aiohttp
import asyncio
from typing import AsyncGenerator
import os
from ..config import config
from .audio_utils import add_wav_header, detect_audio_format

class CosyVoiceClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.get_cosyvoice_url()
    
    async def generate_zero_shot(
        self, 
        text: str, 
        prompt_text: str, 
        prompt_audio_path: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate voice using zero-shot inference
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare form data
                data = aiohttp.FormData()
                data.add_field('tts_text', text)
                data.add_field('prompt_text', prompt_text)
                
                # Add audio file
                with open(prompt_audio_path, 'rb') as f:
                    data.add_field('prompt_wav', f, filename=os.path.basename(prompt_audio_path))
                    
                    # Make request to CosyVoice backend
                    async with session.post(
                        f"{self.base_url}/inference_zero_shot",
                        data=data
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Backend error {response.status}: {error_text}")
                        
                        # Check if response is actually audio
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('audio/'):
                            error_text = await response.text()
                            raise Exception(f"Expected audio response, got {content_type}: {error_text}")
                        
                        # Stream the audio response
                        async for chunk in response.content.iter_chunked(8192):
                            if chunk:  # Only yield non-empty chunks
                                yield chunk
                            
        except Exception as e:
            raise Exception(f"Failed to generate voice: {str(e)}")
    
    async def generate_sft(self, text: str, spk_id: str) -> AsyncGenerator[bytes, None]:
        """
        Generate voice using SFT model
        """
        try:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('tts_text', text)
                data.add_field('spk_id', spk_id)
                
                async with session.post(
                    f"{self.base_url}/inference_sft",
                    data=data
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Backend error: {response.status}")
                    
                    async for chunk in response.content.iter_chunked(8192):
                        yield chunk
                        
        except Exception as e:
            raise Exception(f"Failed to generate voice: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Check if CosyVoice backend is healthy
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/docs") as response:
                    return response.status == 200
        except:
            return False

    async def generate_zero_shot_complete(
        self, 
        text: str, 
        prompt_text: str, 
        prompt_audio_path: str
    ) -> bytes:
        """
        Generate voice using zero-shot inference and return complete audio data
        """
        try:
            print(f"[Client] Connecting to CosyVoice API: {self.base_url}")
            print(f"[Client] Text: {text[:100]}...")
            print(f"[Client] Prompt text: {prompt_text}")
            print(f"[Client] Audio path: {prompt_audio_path}")
            
            async with aiohttp.ClientSession() as session:
                # Prepare form data
                data = aiohttp.FormData()
                data.add_field('tts_text', text)
                data.add_field('prompt_text', prompt_text)
                
                # Add audio file
                with open(prompt_audio_path, 'rb') as f:
                    data.add_field('prompt_wav', f, filename=os.path.basename(prompt_audio_path))
                    
                    print(f"[Client] Sending request to {self.base_url}/inference_zero_shot")
                    
                    # Make request to CosyVoice backend
                    async with session.post(
                        f"{self.base_url}/inference_zero_shot",
                        data=data
                    ) as response:
                        print(f"[Client] Response status: {response.status}")
                        print(f"[Client] Response headers: {dict(response.headers)}")
                        
                        if response.status != 200:
                            try:
                                error_text = await response.text()
                            except:
                                error_text = f"HTTP {response.status} error (unable to decode response)"
                            print(f"[Client] Error response: {error_text}")
                            raise Exception(f"Backend error {response.status}: {error_text}")
                        
                        # Check content type from headers
                        content_type = response.headers.get('content-type', '').lower()
                        print(f"[Client] Content type: '{content_type}'")
                        
                        # If no content-type header, assume it's audio based on successful response
                        if not content_type:
                            print("[Client] No content-type header, assuming audio response")
                            content_type = 'audio/wav'
                        
                        # Read all audio data first
                        raw_audio_data = await response.read()
                        print(f"[Client] Received raw audio data: {len(raw_audio_data)} bytes")
                        
                        # Detect audio format
                        format_info = detect_audio_format(raw_audio_data)
                        print(f"[Client] Audio format detection: {format_info}")
                        
                        # If it's raw PCM data, add WAV header
                        if format_info["format"] == "raw_pcm":
                            print("[Client] Converting raw PCM to WAV format")
                            # CosyVoice typically outputs 22050Hz, mono, 16-bit PCM
                            audio_data = add_wav_header(
                                raw_audio_data, 
                                sample_rate=22050, 
                                channels=1, 
                                bits_per_sample=16
                            )
                            print(f"[Client] WAV file created: {len(audio_data)} bytes (header + {len(raw_audio_data)} data)")
                        else:
                            # Already has proper header
                            audio_data = raw_audio_data
                            print(f"[Client] Using audio data as-is: {format_info['format']} format")
                        
                        # Verify the final result
                        final_format = detect_audio_format(audio_data)
                        print(f"[Client] Final audio format: {final_format}")
                        
                        return audio_data
                            
        except Exception as e:
            print(f"[Client] Exception: {str(e)}")
            raise Exception(f"Failed to generate voice: {str(e)}")
