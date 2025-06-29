"""Scene management for Robot Lady avatar states and content-based automation."""

import logging
from typing import Dict, Optional
from .client import OBSClient


logger = logging.getLogger(__name__)


class SceneManager:
    """Manages OBS scenes and sources for automated streaming."""
    
    def __init__(self, obs_client: OBSClient):
        self.obs_client = obs_client
        self.current_speaker: Optional[str] = None
        self.scene_config = {
            "robot_lady_talking": "Robot Lady Talking",
            "robot_lady_idle": "Robot Lady Idle", 
            "host_only": "Host Only",
            "both_visible": "Both Visible"
        }
    
    def initialize(self):
        """Initialize scene manager and verify scenes exist."""
        try:
            scenes = self.obs_client.get_scene_list()
            available_scenes = [scene['sceneName'] for scene in scenes['scenes']]
            
            # Check if required scenes exist
            missing_scenes = []
            for key, scene_name in self.scene_config.items():
                if scene_name not in available_scenes:
                    missing_scenes.append(scene_name)
            
            if missing_scenes:
                logger.warning(f"Missing scenes: {missing_scenes}")
                logger.info(f"Available scenes: {available_scenes}")
            else:
                logger.info("All required scenes found")
                
        except Exception as e:
            logger.error(f"Failed to initialize scene manager: {e}")
    
    def set_robot_lady_talking(self):
        """Switch to Robot Lady talking state."""
        if self.current_speaker != "robot_lady":
            success = self.obs_client.set_current_scene(
                self.scene_config["robot_lady_talking"]
            )
            if success:
                self.current_speaker = "robot_lady"
                logger.debug("Switched to Robot Lady talking")
    
    def set_robot_lady_idle(self):
        """Switch to Robot Lady idle state."""
        if self.current_speaker == "robot_lady":
            success = self.obs_client.set_current_scene(
                self.scene_config["robot_lady_idle"]
            )
            if success:
                self.current_speaker = None
                logger.debug("Switched to Robot Lady idle")
    
    def set_host_speaking(self):
        """Switch to host speaking state."""
        if self.current_speaker != "host":
            success = self.obs_client.set_current_scene(
                self.scene_config["host_only"]
            )
            if success:
                self.current_speaker = "host"
                logger.debug("Switched to host speaking")
    
    def handle_voice_detection(self, speaker: str, is_speaking: bool):
        """Handle voice detection events and update scenes accordingly."""
        if is_speaking:
            if speaker == "robot_lady":
                self.set_robot_lady_talking()
            elif speaker == "host":
                self.set_host_speaking()
        else:
            if speaker == "robot_lady":
                self.set_robot_lady_idle()
    
    def trigger_content_scene(self, content_type: str):
        """Switch scenes based on content type or keywords."""
        content_scenes = {
            "quote": "Quote Display",
            "book_cover": "Book Display", 
            "timeline": "Timeline View",
            "discussion": self.scene_config["both_visible"]
        }
        
        scene_name = content_scenes.get(content_type)
        if scene_name:
            self.obs_client.set_current_scene(scene_name)
            logger.info(f"Switched to content scene: {scene_name}")
    
    def update_scene_config(self, config: Dict[str, str]):
        """Update scene configuration mapping."""
        self.scene_config.update(config)
        logger.info("Scene configuration updated")