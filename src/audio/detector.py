"""Voice detection system for differentiating between host and Robot Lady."""

import logging
import asyncio
import numpy as np
from typing import Optional, Callable, Dict, Any
import threading
import time
from ..config.settings import settings

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available. Voice detection will be disabled.")


logger = logging.getLogger(__name__)


class VoiceDetector:
    """Detects voice activity and attempts to differentiate speakers."""
    
    def __init__(self):
        self.audio = None
        self.stream = None
        self.running = False
        self.callback: Optional[Callable] = None
        
        # Voice detection parameters
        self.sample_rate = settings.audio.sample_rate
        self.chunk_size = settings.audio.chunk_size
        self.channels = settings.audio.channels
        self.threshold = settings.audio.voice_threshold
        
        # Speaker differentiation
        self.current_speaker = None
        self.last_activity_time = 0
        self.silence_timeout = 2.0  # Seconds of silence before switching to idle
        
        # Simple voice characteristics tracking
        self.voice_profiles = {
            "host": {"avg_pitch": 0, "avg_volume": 0, "sample_count": 0},
            "robot_lady": {"avg_pitch": 0, "avg_volume": 0, "sample_count": 0}
        }
        
        self.detection_thread: Optional[threading.Thread] = None
    
    async def initialize(self) -> bool:
        """Initialize audio system."""
        if not PYAUDIO_AVAILABLE:
            logger.error("PyAudio not available. Cannot initialize voice detection.")
            return False
        
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            device_info = self.audio.get_default_input_device_info()
            logger.info(f"Using audio input device: {device_info['name']}")
            
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Voice detection initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize voice detection: {e}")
            return False
    
    def start_detection(self, callback: Callable[[str, bool], None]):
        """Start voice detection with callback for speaker events."""
        if not self.stream:
            logger.error("Audio stream not initialized")
            return False
        
        self.callback = callback
        self.running = True
        
        # Start detection in separate thread
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        logger.info("Voice detection started")
        return True
    
    def stop_detection(self):
        """Stop voice detection."""
        self.running = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        
        logger.info("Voice detection stopped")
    
    async def stop(self):
        """Async stop method."""
        self.stop_detection()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
    
    def _detection_loop(self):
        """Main detection loop running in separate thread."""
        logger.debug("Voice detection loop started")
        
        while self.running:
            try:
                if not self.stream or self.stream.is_stopped():
                    break
                
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                # Analyze audio
                self._analyze_audio(audio_data)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                break
        
        logger.debug("Voice detection loop ended")
    
    def _analyze_audio(self, audio_data: np.ndarray):
        """Analyze audio data for voice activity and speaker identification."""
        # Calculate volume (RMS)
        volume = np.sqrt(np.mean(audio_data ** 2))
        
        # Voice activity detection
        is_speaking = volume > self.threshold
        current_time = time.time()
        
        if is_speaking:
            self.last_activity_time = current_time
            
            # Simple speaker identification based on audio characteristics
            speaker = self._identify_speaker(audio_data, volume)
            
            # Only trigger callback if speaker changed
            if speaker != self.current_speaker:
                self.current_speaker = speaker
                if self.callback:
                    try:
                        self.callback(speaker, True)
                    except Exception as e:
                        logger.error(f"Error in voice detection callback: {e}")
        
        else:
            # Check for silence timeout
            if (self.current_speaker and 
                current_time - self.last_activity_time > self.silence_timeout):
                
                if self.callback:
                    try:
                        self.callback(self.current_speaker, False)
                    except Exception as e:
                        logger.error(f"Error in silence callback: {e}")
                
                self.current_speaker = None
    
    def _identify_speaker(self, audio_data: np.ndarray, volume: float) -> str:
        """Attempt to identify speaker based on audio characteristics."""
        # Calculate basic audio features
        pitch = self._estimate_pitch(audio_data)
        
        # Simple heuristic-based identification
        # This is a placeholder - in practice, you might use more sophisticated
        # machine learning approaches or voice fingerprinting
        
        # Assume Robot Lady (TTS) has more consistent pitch and volume
        # while human voice has more variation
        variation = np.std(audio_data)
        
        # TTS typically has:
        # - More consistent amplitude
        # - Less natural variation
        # - Different frequency characteristics
        
        if variation < 0.1 and pitch > 150:  # Typical female TTS characteristics
            return "robot_lady"
        else:
            return "host"  # Default to host for human-like variation
    
    def _estimate_pitch(self, audio_data: np.ndarray) -> float:
        """Estimate fundamental frequency (pitch) of audio signal."""
        # Simple autocorrelation-based pitch detection
        # This is a basic implementation - for production, consider using
        # more sophisticated pitch detection algorithms
        
        # Apply windowing
        windowed = audio_data * np.hanning(len(audio_data))
        
        # Autocorrelation
        autocorr = np.correlate(windowed, windowed, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Find peak (excluding zero lag)
        min_period = int(self.sample_rate / 400)  # 400 Hz max
        max_period = int(self.sample_rate / 80)   # 80 Hz min
        
        if len(autocorr) > max_period:
            peak_idx = np.argmax(autocorr[min_period:max_period]) + min_period
            if peak_idx > 0:
                return self.sample_rate / peak_idx
        
        return 0.0  # Unable to detect pitch
    
    def calibrate_speaker(self, speaker_name: str, duration: float = 5.0):
        """Calibrate voice profile for a specific speaker."""
        logger.info(f"Calibrating voice profile for {speaker_name} for {duration} seconds...")
        
        if not self.stream:
            logger.error("Audio stream not initialized")
            return False
        
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < duration:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                volume = np.sqrt(np.mean(audio_data ** 2))
                if volume > self.threshold:  # Only collect samples with voice activity
                    pitch = self._estimate_pitch(audio_data)
                    samples.append({"pitch": pitch, "volume": volume})
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error during calibration: {e}")
                break
        
        if samples:
            # Update voice profile
            avg_pitch = np.mean([s["pitch"] for s in samples])
            avg_volume = np.mean([s["volume"] for s in samples])
            
            self.voice_profiles[speaker_name] = {
                "avg_pitch": avg_pitch,
                "avg_volume": avg_volume,
                "sample_count": len(samples)
            }
            
            logger.info(f"Calibration complete for {speaker_name}: "
                       f"avg_pitch={avg_pitch:.1f}Hz, avg_volume={avg_volume:.3f}")
            return True
        else:
            logger.warning(f"No voice samples collected for {speaker_name}")
            return False
    
    def get_voice_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get current voice profiles."""
        return self.voice_profiles.copy()
    
    def set_threshold(self, threshold: float):
        """Update voice activity threshold."""
        self.threshold = threshold
        logger.info(f"Voice threshold updated to {threshold}")