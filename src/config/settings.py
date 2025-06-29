"""Configuration settings for Sserf automation system."""

import os
from typing import Optional
from pydantic import BaseSettings


class OBSSettings(BaseSettings):
    """OBS WebSocket connection settings."""
    host: str = "localhost"
    port: int = 4455
    password: Optional[str] = None
    
    class Config:
        env_prefix = "OBS_"


class ThumbnailSettings(BaseSettings):
    """Thumbnail generation settings."""
    width: int = 1280
    height: int = 720
    output_dir: str = "thumbnails"
    template_bg: str = "assets/background.jpg"
    avatar_left: str = "assets/robot_lady.png"
    avatar_right: str = "assets/host.png"
    
    # Font settings
    title_font_size: int = 72
    subtitle_font_size: int = 48
    year_font_size: int = 64
    
    # Colors
    title_color: str = "#00FF7F"  # Green from your thumbnail
    outline_color: str = "#000000"  # Black outline
    year_color: str = "#FFFFFF"  # White
    
    class Config:
        env_prefix = "THUMBNAIL_"


class AudioSettings(BaseSettings):
    """Audio processing settings."""
    sample_rate: int = 44100
    chunk_size: int = 1024
    channels: int = 1
    voice_threshold: float = 0.01
    
    class Config:
        env_prefix = "AUDIO_"


class AppSettings(BaseSettings):
    """Main application settings."""
    obs: OBSSettings = OBSSettings()
    thumbnail: ThumbnailSettings = ThumbnailSettings()
    audio: AudioSettings = AudioSettings()
    
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = AppSettings()