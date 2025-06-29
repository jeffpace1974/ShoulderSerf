"""Main entry point for Sserf C.S. Lewis streaming automation system."""

import logging
import asyncio
import signal
import sys
from pathlib import Path
from src.config.settings import settings
from src.obs.client import OBSClient
from src.obs.scene_manager import SceneManager
from src.thumbnail.generator import ThumbnailGenerator
from src.audio.detector import VoiceDetector
from src.automation.controller import AutomationController


# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sserf.log')
    ]
)

logger = logging.getLogger(__name__)


class SserfApp:
    """Main application controller for Sserf automation system."""
    
    def __init__(self):
        self.obs_client = OBSClient()
        self.scene_manager = SceneManager(self.obs_client)
        self.thumbnail_generator = ThumbnailGenerator()
        self.voice_detector = None
        self.automation_controller = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing Sserf automation system...")
        
        # Connect to OBS
        if not self.obs_client.connect():
            logger.error("Failed to connect to OBS. Please ensure OBS is running with WebSocket enabled.")
            return False
        
        # Initialize scene manager
        self.scene_manager.initialize()
        
        # Initialize voice detector
        try:
            from src.audio.detector import VoiceDetector
            self.voice_detector = VoiceDetector()
            await self.voice_detector.initialize()
        except Exception as e:
            logger.warning(f"Voice detector initialization failed: {e}")
            logger.info("Continuing without voice detection...")
        
        # Initialize automation controller
        from src.automation.controller import AutomationController
        self.automation_controller = AutomationController(
            self.obs_client,
            self.scene_manager,
            self.voice_detector
        )
        
        logger.info("Sserf initialization complete!")
        return True
    
    async def run(self):
        """Main application loop."""
        if not await self.initialize():
            return
        
        self.running = True
        
        try:
            logger.info("Sserf is running. Press Ctrl+C to stop.")
            
            # Start automation controller
            if self.automation_controller:
                await self.automation_controller.start()
            
            # Main loop - keep running until shutdown
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown all components."""
        logger.info("Shutting down Sserf...")
        
        self.running = False
        
        if self.automation_controller:
            await self.automation_controller.stop()
        
        if self.voice_detector:
            await self.voice_detector.stop()
        
        if self.obs_client:
            self.obs_client.disconnect()
        
        logger.info("Sserf shutdown complete")
    
    def generate_thumbnail(self, title: str, year: str, output_filename: str = None):
        """Generate a thumbnail with the specified title and year."""
        try:
            output_path = self.thumbnail_generator.generate_thumbnail(
                title, year, output_filename=output_filename
            )
            logger.info(f"Thumbnail generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            return None
    
    def generate_thumbnail_from_content(self, lewis_text: str, context: str = ""):
        """Generate thumbnail based on Lewis text content."""
        try:
            output_path = self.thumbnail_generator.generate_from_content(lewis_text, context)
            logger.info(f"Content-based thumbnail generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate content-based thumbnail: {e}")
            return None


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


async def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run application
    app = SserfApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)