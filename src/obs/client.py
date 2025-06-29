"""OBS WebSocket client for scene and source management using obsws-python."""

import logging
from typing import Optional, Dict, Any
import obsws_python as obs
from ..config.settings import settings


logger = logging.getLogger(__name__)


class OBSClient:
    """OBS WebSocket client for automating scene management using obsws-python library."""
    
    def __init__(self):
        self.client: Optional[obs.ReqClient] = None
        self.event_client: Optional[obs.EventClient] = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to OBS WebSocket server."""
        try:
            # Create request client for sending commands
            self.client = obs.ReqClient(
                host=settings.obs.host,
                port=settings.obs.port,
                password=settings.obs.password,
                timeout=3
            )
            
            # Create event client for receiving events
            self.event_client = obs.EventClient(
                host=settings.obs.host,
                port=settings.obs.port,
                password=settings.obs.password
            )
            
            # Test connection by getting version info
            version_info = self.client.get_version()
            logger.info(f"Connected to OBS Studio {version_info.obs_version}")
            logger.info(f"OBS WebSocket version: {version_info.obs_web_socket_version}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to OBS: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket server."""
        if self.client:
            self.client.disconnect()
        if self.event_client:
            self.event_client.disconnect()
        self.connected = False
        logger.info("Disconnected from OBS")
    
    def get_scene_list(self) -> Dict[str, Any]:
        """Get list of available scenes."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        response = self.client.get_scene_list()
        return {
            "scenes": [{"sceneName": scene.scene_name} for scene in response.scenes],
            "currentProgramSceneName": response.current_program_scene_name
        }
    
    def get_current_scene(self) -> str:
        """Get current active scene name."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        response = self.client.get_current_program_scene()
        return response.scene_name
    
    def set_current_scene(self, scene_name: str) -> bool:
        """Switch to specified scene."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            self.client.set_current_program_scene(scene_name)
            logger.info(f"Switched to scene: {scene_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to scene {scene_name}: {e}")
            return False
    
    def set_scene_item_enabled(self, scene_name: str, item_name: str, enabled: bool) -> bool:
        """Enable or disable a scene item."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            # First get the scene item ID
            scene_items = self.client.get_scene_item_list(scene_name)
            
            # Find the item by name
            item_id = None
            for item in scene_items.scene_items:
                if item.source_name == item_name:
                    item_id = item.scene_item_id
                    break
            
            if item_id is None:
                logger.error(f"Scene item '{item_name}' not found in scene '{scene_name}'")
                return False
            
            self.client.set_scene_item_enabled(scene_name, item_id, enabled)
            logger.info(f"Set {item_name} enabled to {enabled} in scene {scene_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set scene item enabled: {e}")
            return False
    
    def get_input_list(self) -> Dict[str, Any]:
        """Get list of available inputs/sources."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        response = self.client.get_input_list()
        return {
            "inputs": [{"inputName": inp.input_name, "inputKind": inp.input_kind} 
                      for inp in response.inputs]
        }
    
    def start_recording(self) -> bool:
        """Start recording."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            self.client.start_record()
            logger.info("Recording started")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            self.client.stop_record()
            logger.info("Recording stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    def start_streaming(self) -> bool:
        """Start streaming."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            self.client.start_stream()
            logger.info("Streaming started")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self) -> bool:
        """Stop streaming."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        try:
            self.client.stop_stream()
            logger.info("Streaming stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False
    
    def register_event_callback(self, event_name: str, callback):
        """Register a callback for OBS events."""
        if not self.event_client:
            raise ConnectionError("Event client not connected")
        
        # Register callback using the event client
        self.event_client.callback.register(callback)
        logger.info(f"Registered callback for event: {event_name}")
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get current stream status."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to OBS")
        
        response = self.client.get_stream_status()
        return {
            "outputActive": response.output_active,
            "outputReconnecting": response.output_reconnecting,
            "outputTimecode": response.output_timecode,
            "outputDuration": response.output_duration,
            "outputCongestion": response.output_congestion,
            "outputBytes": response.output_bytes,
            "outputSkippedFrames": response.output_skipped_frames,
            "outputTotalFrames": response.output_total_frames
        }