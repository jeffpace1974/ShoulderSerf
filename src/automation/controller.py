"""Main automation controller coordinating all subsystems."""

import logging
import asyncio
from typing import Optional, Dict, Any
from ..obs.client import OBSClient
from ..obs.scene_manager import SceneManager
from ..audio.detector import VoiceDetector


logger = logging.getLogger(__name__)


class AutomationController:
    """Main controller for coordinating OBS automation and voice detection."""
    
    def __init__(self, obs_client: OBSClient, scene_manager: SceneManager, 
                 voice_detector: Optional[VoiceDetector] = None):
        self.obs_client = obs_client
        self.scene_manager = scene_manager
        self.voice_detector = voice_detector
        self.running = False
        
        # State tracking
        self.current_automation_mode = "auto"  # auto, manual, voice_only
        self.last_scene_change = 0
        self.scene_change_cooldown = 1.0  # Minimum seconds between scene changes
        
        # Event handlers
        self.event_handlers = {
            "voice_detected": self._handle_voice_event,
            "scene_changed": self._handle_scene_change,
            "stream_started": self._handle_stream_start,
            "stream_stopped": self._handle_stream_stop
        }
    
    async def start(self):
        """Start the automation controller."""
        logger.info("Starting automation controller...")
        
        self.running = True
        
        # Start voice detection if available
        if self.voice_detector:
            success = self.voice_detector.start_detection(self._on_voice_event)
            if success:
                logger.info("Voice detection started")
            else:
                logger.warning("Failed to start voice detection")
        
        # Register OBS event callbacks if available
        try:
            if self.obs_client.event_client:
                self.obs_client.register_event_callback("scene_changed", self._on_scene_change)
                logger.info("OBS event callbacks registered")
        except Exception as e:
            logger.warning(f"Failed to register OBS event callbacks: {e}")
        
        logger.info("Automation controller started")
    
    async def stop(self):
        """Stop the automation controller."""
        logger.info("Stopping automation controller...")
        
        self.running = False
        
        if self.voice_detector:
            self.voice_detector.stop_detection()
        
        logger.info("Automation controller stopped")
    
    def _on_voice_event(self, speaker: str, is_speaking: bool):
        """Handle voice detection events."""
        if not self.running:
            return
        
        logger.debug(f"Voice event: {speaker} {'speaking' if is_speaking else 'stopped'}")
        
        # Handle voice events through the event system
        asyncio.create_task(self._handle_voice_event(speaker, is_speaking))
    
    def _on_scene_change(self, event_data):
        """Handle OBS scene change events."""
        if not self.running:
            return
        
        logger.debug(f"Scene changed: {event_data}")
        asyncio.create_task(self._handle_scene_change(event_data))
    
    async def _handle_voice_event(self, speaker: str, is_speaking: bool):
        """Process voice detection events and trigger scene changes."""
        import time
        
        # Implement cooldown to prevent rapid scene switching
        current_time = time.time()
        if current_time - self.last_scene_change < self.scene_change_cooldown:
            return
        
        # Only process if in auto or voice_only mode
        if self.current_automation_mode not in ["auto", "voice_only"]:
            return
        
        try:
            # Delegate to scene manager
            self.scene_manager.handle_voice_detection(speaker, is_speaking)
            self.last_scene_change = current_time
            
        except Exception as e:
            logger.error(f"Error handling voice event: {e}")
    
    async def _handle_scene_change(self, event_data):
        """Handle OBS scene change events."""
        logger.debug(f"Processing scene change: {event_data}")
        # Add any post-scene-change logic here
    
    async def _handle_stream_start(self, event_data):
        """Handle stream start events."""
        logger.info("Stream started - enabling full automation")
        self.current_automation_mode = "auto"
    
    async def _handle_stream_stop(self, event_data):
        """Handle stream stop events."""
        logger.info("Stream stopped - switching to manual mode")
        self.current_automation_mode = "manual"
    
    def set_automation_mode(self, mode: str):
        """Set automation mode: auto, manual, voice_only."""
        if mode in ["auto", "manual", "voice_only"]:
            self.current_automation_mode = mode
            logger.info(f"Automation mode set to: {mode}")
        else:
            logger.warning(f"Invalid automation mode: {mode}")
    
    def trigger_scene_change(self, scene_name: str):
        """Manually trigger a scene change."""
        try:
            success = self.obs_client.set_current_scene(scene_name)
            if success:
                logger.info(f"Manually triggered scene change to: {scene_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to trigger scene change: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "running": self.running,
            "automation_mode": self.current_automation_mode,
            "obs_connected": self.obs_client.connected,
            "voice_detection_active": self.voice_detector is not None and self.voice_detector.running if self.voice_detector else False,
            "current_scene": self.obs_client.get_current_scene() if self.obs_client.connected else None,
            "scene_manager_speaker": self.scene_manager.current_speaker
        }
    
    def calibrate_voice_detection(self, speaker: str, duration: float = 5.0):
        """Calibrate voice detection for a specific speaker."""
        if not self.voice_detector:
            logger.error("Voice detector not available")
            return False
        
        logger.info(f"Starting voice calibration for {speaker}")
        return self.voice_detector.calibrate_speaker(speaker, duration)
    
    def set_voice_threshold(self, threshold: float):
        """Set voice detection threshold."""
        if self.voice_detector:
            self.voice_detector.set_threshold(threshold)
            logger.info(f"Voice threshold set to {threshold}")
        else:
            logger.warning("Voice detector not available")
    
    async def test_scene_switching(self):
        """Test scene switching functionality."""
        if not self.obs_client.connected:
            logger.error("OBS not connected - cannot test scene switching")
            return False
        
        try:
            # Get available scenes
            scenes = self.obs_client.get_scene_list()
            scene_names = [scene["sceneName"] for scene in scenes["scenes"]]
            
            logger.info(f"Available scenes: {scene_names}")
            
            # Test switching to each configured scene
            for scene_key, scene_name in self.scene_manager.scene_config.items():
                if scene_name in scene_names:
                    logger.info(f"Testing scene: {scene_name}")
                    success = self.obs_client.set_current_scene(scene_name)
                    if success:
                        logger.info(f"✓ Successfully switched to {scene_name}")
                    else:
                        logger.error(f"✗ Failed to switch to {scene_name}")
                    
                    # Wait between switches
                    await asyncio.sleep(2)
                else:
                    logger.warning(f"Scene '{scene_name}' not found in OBS")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during scene switching test: {e}")
            return False