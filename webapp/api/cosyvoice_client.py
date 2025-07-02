"""
Client for communicating with CosyVoice FastAPI backend
"""

import aiohttp
import asyncio
import requests  # Add requests as fallback
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
        prompt_audio_path: str,
        max_retries: int = 2
    ) -> bytes:
        """
        Generate voice using zero-shot inference and return complete audio data
        """
        for attempt in range(max_retries + 1):
            try:
                print(f"[Client] Attempt {attempt + 1}/{max_retries + 1}")
                return await self._generate_zero_shot_attempt(text, prompt_text, prompt_audio_path)
            except Exception as e:
                error_msg = str(e).lower()
                print(f"[Client] Attempt {attempt + 1} failed: {str(e)}")
                
                # If it's a transfer encoding error, try sync fallback immediately
                if 'transferencodingerror' in error_msg or 'transfer length' in error_msg:
                    print("[Client] Transfer encoding error detected, trying sync fallback")
                    try:
                        # Run sync method in thread pool to avoid blocking
                        import concurrent.futures
                        loop = asyncio.get_event_loop()
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            result = await loop.run_in_executor(
                                executor, 
                                self._generate_zero_shot_sync_fallback,
                                text, prompt_text, prompt_audio_path
                            )
                            return result
                    except Exception as sync_error:
                        print(f"[Client] Sync fallback also failed: {sync_error}")
                
                if attempt == max_retries:
                    raise e
                print(f"[Client] Retrying in 2 seconds...")
                await asyncio.sleep(2)
    
    def _generate_zero_shot_sync_fallback(
        self, 
        text: str, 
        prompt_text: str, 
        prompt_audio_path: str
    ) -> bytes:
        """
        Synchronous fallback method using requests library
        """
        try:
            print("[Client] Using synchronous fallback method with requests")
            
            # Prepare form data for requests
            files = {
                'tts_text': (None, text),
                'prompt_text': (None, prompt_text),
                'prompt_wav': (os.path.basename(prompt_audio_path), open(prompt_audio_path, 'rb'), 'audio/wav')
            }
            
            # Make request with requests library
            response = requests.post(
                f"{self.base_url}/inference_zero_shot",
                files=files,
                timeout=120,
                stream=True
            )
            
            print(f"[Client] Sync response status: {response.status_code}")
            print(f"[Client] Sync response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                raise Exception(f"Backend error {response.status_code}: {response.text}")
            
            # Read response content
            raw_audio_data = response.content
            print(f"[Client] Sync received audio data: {len(raw_audio_data)} bytes")
            
            # Close the file handle
            files['prompt_wav'][1].close()
            
            return raw_audio_data
            
        except Exception as e:
            print(f"[Client] Sync fallback failed: {str(e)}")
            raise e
    
    async def _generate_zero_shot_attempt(
        self, 
        text: str, 
        prompt_text: str, 
        prompt_audio_path: str
    ) -> bytes:
        try:
            print(f"[Client] Connecting to CosyVoice API: {self.base_url}")
            print(f"[Client] Text: {text[:100]}...")
            print(f"[Client] Prompt text: {prompt_text}")
            print(f"[Client] Audio path: {prompt_audio_path}")
            
            # Create a more tolerant connector for handling problematic responses
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=120, connect=30)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'Connection': 'close'}  # Force connection close to avoid keep-alive issues
            ) as session:
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
                        
                        # Read all audio data with robust error handling
                        raw_audio_data = b''
                        try:
                            # Try to read all data at once first
                            raw_audio_data = await response.read()
                            print(f"[Client] Received raw audio data: {len(raw_audio_data)} bytes")
                        except Exception as read_error:
                            print(f"[Client] Error reading response data: {read_error}")
                            # Try to read in chunks to handle transfer encoding issues
                            try:
                                print("[Client] Attempting to read response in chunks...")
                                chunk_data = []
                                async for chunk in response.content.iter_chunked(8192):
                                    chunk_data.append(chunk)
                                raw_audio_data = b''.join(chunk_data)
                                print(f"[Client] Successfully read {len(raw_audio_data)} bytes in chunks")
                            except Exception as chunk_error:
                                print(f"[Client] Chunk reading also failed: {chunk_error}")
                                # Last resort: try to get whatever data is available
                                try:
                                    raw_audio_data = await response.content.read()
                                    print(f"[Client] Fallback read got {len(raw_audio_data)} bytes")
                                except Exception as fallback_error:
                                    raise Exception(f"Failed to read response data: {read_error}, chunk error: {chunk_error}, fallback error: {fallback_error}")
                        
                        if len(raw_audio_data) == 0:
                            raise Exception("Received empty response from CosyVoice backend")
                        
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
