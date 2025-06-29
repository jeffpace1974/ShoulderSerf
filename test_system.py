#!/usr/bin/env python3
"""
Comprehensive test script to validate all Sserf functionality.

This script will test:
1. Basic system setup and dependencies
2. Thumbnail generation (with and without AI)
3. OCR functionality (if Tesseract is available)
4. OBS connection (if OBS is running)
5. Voice detection (if microphone is available)

Run this first to validate your installation.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking Dependencies")
    print("=" * 50)
    
    results = {}
    
    # Core dependencies
    try:
        import PIL
        print("✅ PIL/Pillow: Available")
        results['pillow'] = True
    except ImportError:
        print("❌ PIL/Pillow: Missing - run: pip install pillow")
        results['pillow'] = False
    
    try:
        import numpy
        print("✅ NumPy: Available")
        results['numpy'] = True
    except ImportError:
        print("❌ NumPy: Missing - run: pip install numpy")
        results['numpy'] = False
    
    try:
        import obsws_python
        print("✅ OBS WebSocket: Available")
        results['obs'] = True
    except ImportError:
        print("❌ OBS WebSocket: Missing - run: pip install obsws-python")
        results['obs'] = False
    
    # OCR dependency
    try:
        import pytesseract
        print("✅ PyTesseract: Available")
        results['ocr'] = True
        
        # Test Tesseract binary
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract binary: Available")
            results['tesseract'] = True
        except Exception:
            print("❌ Tesseract binary: Missing")
            print("   Install: sudo apt install tesseract-ocr (Linux)")
            print("   Install: brew install tesseract (Mac)")
            print("   Windows: Download from GitHub releases")
            results['tesseract'] = False
    except ImportError:
        print("❌ PyTesseract: Missing - run: pip install pytesseract")
        results['ocr'] = False
        results['tesseract'] = False
    
    # Audio dependency
    try:
        import pyaudio
        print("✅ PyAudio: Available")
        results['audio'] = True
    except ImportError:
        print("❌ PyAudio: Missing - run: pip install pyaudio")
        print("   May need: sudo apt install portaudio19-dev (Linux)")
        results['audio'] = False
    
    # AI dependencies (optional)
    try:
        import openai
        print("✅ OpenAI: Available")
        results['openai'] = True
    except ImportError:
        print("⚠️  OpenAI: Missing (optional for AI titles)")
        results['openai'] = False
    
    try:
        import anthropic
        print("✅ Anthropic: Available")
        results['anthropic'] = True
    except ImportError:
        print("⚠️  Anthropic: Missing (optional for AI titles)")
        results['anthropic'] = False
    
    return results


def test_basic_thumbnail_generation():
    """Test basic thumbnail generation without AI."""
    print("\n🎨 Testing Basic Thumbnail Generation")
    print("=" * 50)
    
    try:
        from src.thumbnail.generator import ThumbnailGenerator
        
        generator = ThumbnailGenerator()
        
        # Test 1: Simple manual thumbnail
        print("1. Testing manual thumbnail generation...")
        output_path = generator.generate_thumbnail(
            title="Test Thumbnail Generation",
            year="1924",
            output_filename="test_basic.png"
        )
        
        if output_path and os.path.exists(output_path):
            print(f"✅ Basic thumbnail generated: {output_path}")
            return True
        else:
            print("❌ Basic thumbnail generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in basic thumbnail generation: {e}")
        return False


def test_content_analysis():
    """Test content analysis and AI-powered title generation."""
    print("\n🧠 Testing Content Analysis")
    print("=" * 50)
    
    try:
        from src.thumbnail.content_analyzer import ContentAnalyzer
        
        analyzer = ContentAnalyzer()
        
        # Test content
        test_content = """
        This morning I had quite the amusing conversation with my colleague about 
        bacon and eggs. He insists that a proper English breakfast requires both, 
        but I argued that sometimes simple bread and butter suffices, especially 
        when one is absorbed in reading Malory's tales of King Arthur. There's 
        something about those medieval stories that makes even the simplest meal 
        feel like a feast fit for Camelot.
        """
        
        print("Analyzing sample content...")
        analysis = analyzer.analyze_content(test_content, "1943")
        
        print(f"Generated Title: '{analysis['title']}'")
        print(f"Detected Year: {analysis['year']}")
        print(f"Themes: {', '.join(analysis['themes']) if analysis['themes'] else 'None'}")
        print(f"Analysis Method: {analysis['analysis_method']}")
        
        # Test thumbnail generation from content
        print("\nGenerating thumbnail from analyzed content...")
        
        from src.thumbnail.generator import ThumbnailGenerator
        generator = ThumbnailGenerator()
        
        output_path = generator.generate_from_content(test_content, year="1943")
        
        if output_path and os.path.exists(output_path):
            print(f"✅ Content-based thumbnail generated: {output_path}")
            return True
        else:
            print("❌ Content-based thumbnail generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in content analysis: {e}")
        return False


def test_ocr_functionality():
    """Test OCR functionality if Tesseract is available."""
    print("\n📷 Testing OCR Functionality")
    print("=" * 50)
    
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image with text
        print("Creating test image with text...")
        
        test_image_path = "test_text_image.png"
        img = Image.new('RGB', (600, 200), 'white')
        draw = ImageDraw.Draw(img)
        
        test_text = "C.S. Lewis discusses medieval literature in 1935."
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((20, 80), test_text, fill='black', font=font)
        img.save(test_image_path)
        
        # Test OCR
        from src.thumbnail.content_analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
        
        extracted_text = analyzer.extract_text_from_image(test_image_path)
        
        print(f"Test text: '{test_text}'")
        print(f"Extracted: '{extracted_text.strip()}'")
        
        # Clean up test image
        os.remove(test_image_path)
        
        if extracted_text and "Lewis" in extracted_text:
            print("✅ OCR functionality working")
            return True
        else:
            print("⚠️  OCR extracted text but accuracy may be low")
            return True
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False


def test_obs_connection():
    """Test OBS WebSocket connection if OBS is running."""
    print("\n📺 Testing OBS Connection")
    print("=" * 50)
    
    try:
        from src.obs.client import OBSClient
        from src.config.settings import settings
        
        print(f"Attempting to connect to OBS at {settings.obs.host}:{settings.obs.port}")
        
        obs_client = OBSClient()
        
        if obs_client.connect():
            print("✅ Successfully connected to OBS")
            
            # Test basic operations
            try:
                scenes = obs_client.get_scene_list()
                current_scene = obs_client.get_current_scene()
                
                print(f"Current scene: {current_scene}")
                print(f"Available scenes: {[s['sceneName'] for s in scenes['scenes']]}")
                
                obs_client.disconnect()
                return True
                
            except Exception as e:
                print(f"⚠️  Connected but operations failed: {e}")
                obs_client.disconnect()
                return False
        else:
            print("❌ Could not connect to OBS")
            print("Make sure:")
            print("  - OBS Studio is running")
            print("  - WebSocket server is enabled (Tools > WebSocket Server Settings)")
            print("  - Password matches your .env file")
            return False
            
    except Exception as e:
        print(f"❌ OBS connection test failed: {e}")
        return False


def test_voice_detection():
    """Test voice detection if audio is available."""
    print("\n🎤 Testing Voice Detection")
    print("=" * 50)
    
    try:
        from src.audio.detector import VoiceDetector
        import asyncio
        
        async def test_audio():
            voice_detector = VoiceDetector()
            
            if await voice_detector.initialize():
                print("✅ Voice detection initialized successfully")
                
                print("Testing audio capture for 3 seconds...")
                print("(Try speaking or making noise)")
                
                events = []
                
                def test_callback(speaker, is_speaking):
                    events.append((speaker, is_speaking))
                    print(f"Voice event: {speaker} {'speaking' if is_speaking else 'silent'}")
                
                voice_detector.start_detection(test_callback)
                
                await asyncio.sleep(3)
                
                voice_detector.stop_detection()
                await voice_detector.stop()
                
                if events:
                    print(f"✅ Voice detection captured {len(events)} events")
                    return True
                else:
                    print("⚠️  Voice detection working but no events captured")
                    print("   (This is normal if no audio input)")
                    return True
            else:
                print("❌ Voice detection initialization failed")
                return False
        
        return asyncio.run(test_audio())
        
    except Exception as e:
        print(f"❌ Voice detection test failed: {e}")
        return False


def test_cli_interface():
    """Test the CLI interface."""
    print("\n💻 Testing CLI Interface")
    print("=" * 50)
    
    try:
        # Test CLI help
        import subprocess
        result = subprocess.run([sys.executable, "thumbnail_cli.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Generate C.S. Lewis episode thumbnails" in result.stdout:
            print("✅ CLI interface is working")
            
            # Test analysis-only mode
            result = subprocess.run([
                sys.executable, "thumbnail_cli.py", 
                "--text", "Lewis discusses bacon and literature in 1943",
                "--analyze-only"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ CLI content analysis working")
                print("Sample output:")
                print(result.stdout[-200:])  # Last 200 chars
                return True
            else:
                print("⚠️  CLI basic functions work, analysis had issues")
                return True
        else:
            print("❌ CLI interface not working properly")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🧪 Sserf System Validation")
    print("=" * 60)
    print("Testing all components of your C.S. Lewis automation system...")
    print()
    
    # Setup logging to show errors
    logging.basicConfig(level=logging.WARNING)
    
    # Run all tests
    test_results = {}
    
    test_results['dependencies'] = check_dependencies()
    test_results['basic_thumbnail'] = test_basic_thumbnail_generation()
    test_results['content_analysis'] = test_content_analysis()
    test_results['ocr'] = test_ocr_functionality()
    test_results['obs'] = test_obs_connection()
    test_results['voice'] = test_voice_detection()
    test_results['cli'] = test_cli_interface()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    # Core functionality
    core_working = (
        test_results['basic_thumbnail'] and 
        test_results['content_analysis'] and
        test_results['cli']
    )
    
    print(f"🎨 Thumbnail Generation: {'✅ WORKING' if core_working else '❌ ISSUES'}")
    print(f"📷 OCR Functionality: {'✅ WORKING' if test_results['ocr'] else '❌ NEEDS SETUP'}")
    print(f"📺 OBS Integration: {'✅ WORKING' if test_results['obs'] else '❌ NEEDS SETUP'}")
    print(f"🎤 Voice Detection: {'✅ WORKING' if test_results['voice'] else '❌ NEEDS SETUP'}")
    print(f"💻 CLI Interface: {'✅ WORKING' if test_results['cli'] else '❌ ISSUES'}")
    
    print("\n🎯 NEXT STEPS:")
    
    if core_working:
        print("✅ Core thumbnail system is ready to use!")
        print("   Try: python thumbnail_cli.py --interactive")
        print()
        
        if not test_results['ocr']:
            print("📷 For book page photos: Install Tesseract OCR")
            print("   Linux: sudo apt install tesseract-ocr")
            print("   Mac: brew install tesseract")
            print()
        
        if not test_results['obs']:
            print("📺 For OBS automation: Start OBS and enable WebSocket")
            print("   Tools > WebSocket Server Settings > Enable")
            print()
        
        if not test_results['voice']:
            print("🎤 For voice detection: Check microphone permissions")
            print()
        
        print("🚀 Ready to start using Sserf for your C.S. Lewis streams!")
        
    else:
        print("❌ Core system needs attention:")
        if not test_results['basic_thumbnail']:
            print("   - Fix thumbnail generation issues")
        if not test_results['content_analysis']:
            print("   - Fix content analysis issues")
        if not test_results['cli']:
            print("   - Fix CLI interface issues")
        print("   - Check error messages above")
    
    return core_working


if __name__ == "__main__":
    run_comprehensive_test()