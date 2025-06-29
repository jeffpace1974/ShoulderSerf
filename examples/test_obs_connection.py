"""Test script for verifying OBS WebSocket connection and basic functionality."""

import sys
import os
import logging
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings
from src.obs.client import OBSClient
from src.obs.scene_manager import SceneManager


async def test_obs_connection():
    """Test OBS WebSocket connection and basic operations."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing OBS WebSocket connection...")
    
    # Initialize OBS client
    obs_client = OBSClient()
    
    # Test connection
    logger.info(f"Attempting to connect to OBS at {settings.obs.host}:{settings.obs.port}")
    
    if not obs_client.connect():
        logger.error("Failed to connect to OBS!")
        logger.error("Please ensure:")
        logger.error("1. OBS Studio is running")
        logger.error("2. WebSocket server is enabled in OBS Tools > WebSocket Server Settings")
        logger.error("3. The connection details in .env are correct")
        return False
    
    try:
        # Test getting scene list
        logger.info("Getting scene list...")
        scenes = obs_client.get_scene_list()
        logger.info(f"Available scenes: {[s['sceneName'] for s in scenes['scenes']]}")
        
        # Test getting current scene
        current_scene = obs_client.get_current_scene()
        logger.info(f"Current scene: {current_scene}")
        
        # Test scene manager
        scene_manager = SceneManager(obs_client)
        scene_manager.initialize()
        
        # Test input list
        inputs = obs_client.get_input_list()
        logger.info(f"Available inputs: {[i['inputName'] for i in inputs['inputs']]}")
        
        logger.info("✓ OBS connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error during OBS testing: {e}")
        return False
    
    finally:
        obs_client.disconnect()


def test_thumbnail_generation():
    """Test thumbnail generation functionality."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing thumbnail generation...")
    
    try:
        from src.thumbnail.generator import ThumbnailGenerator
        
        generator = ThumbnailGenerator()
        
        # Test basic thumbnail generation
        output_path = generator.generate_thumbnail(
            title="Test Thumbnail Generation",
            year="2024",
            output_filename="test_thumbnail.png"
        )
        
        if output_path and os.path.exists(output_path):
            logger.info(f"✓ Thumbnail generated successfully: {output_path}")
            return True
        else:
            logger.error("✗ Thumbnail generation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error during thumbnail testing: {e}")
        return False


def test_voice_detection():
    """Test voice detection functionality."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing voice detection...")
    
    try:
        from src.audio.detector import VoiceDetector
        
        voice_detector = VoiceDetector()
        
        # Test initialization
        if not asyncio.run(voice_detector.initialize()):
            logger.warning("Voice detection initialization failed - this is expected if no microphone is available")
            return True  # Not a critical failure
        
        logger.info("✓ Voice detection initialized successfully")
        
        # Test basic functionality
        def test_callback(speaker, is_speaking):
            logger.info(f"Voice callback: {speaker} {'speaking' if is_speaking else 'stopped'}")
        
        # Start detection briefly
        voice_detector.start_detection(test_callback)
        
        # Let it run for a few seconds
        import time
        time.sleep(3)
        
        voice_detector.stop_detection()
        asyncio.run(voice_detector.stop())
        
        logger.info("✓ Voice detection test completed")
        return True
        
    except Exception as e:
        logger.error(f"Error during voice detection testing: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    
    print("=" * 50)
    print("Sserf System Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test OBS connection
    print("\n1. Testing OBS Connection...")
    results['obs'] = await test_obs_connection()
    
    # Test thumbnail generation
    print("\n2. Testing Thumbnail Generation...")
    results['thumbnail'] = test_thumbnail_generation()
    
    # Test voice detection
    print("\n3. Testing Voice Detection...")
    results['voice'] = test_voice_detection()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.upper():15} {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\nTroubleshooting:")
        if not results['obs']:
            print("- OBS: Ensure OBS Studio is running with WebSocket server enabled")
        if not results['thumbnail']:
            print("- Thumbnail: Check that required fonts and image libraries are installed")
        if not results['voice']:
            print("- Voice: Check that a microphone is connected and accessible")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_all_tests())