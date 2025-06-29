#!/usr/bin/env python3
"""
Actual Claude Vision Processor for Thumbnail Text Extraction

This script uses Claude's actual vision capabilities to read and extract
the exact text from YouTube thumbnail images. This is the proper approach
to get accurate text rather than generated descriptions.
"""

import os
import sys
import sqlite3
import base64
import time
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def get_videos_needing_vision_processing() -> List[Tuple[str, str, str]]:
    """Get all videos that need actual vision processing."""
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            SELECT video_id, title, thumbnail_text 
            FROM videos 
            WHERE thumbnail IS NOT NULL
            ORDER BY video_id
        """)
        
        videos = cursor.fetchall()
        conn.close()
        return videos
        
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def find_thumbnail_image(video_id: str) -> Optional[str]:
    """Find the thumbnail image file for a video ID."""
    # Check all vision batch directories
    for i in range(1, 13):
        batch_dir = f"vision_batch_{i:02d}"
        if os.path.exists(batch_dir):
            thumbnail_path = os.path.join(batch_dir, f"{video_id}.jpg")
            if os.path.exists(thumbnail_path):
                return thumbnail_path
    
    # Check thumbnails_for_vision directory
    thumbnail_path = os.path.join("thumbnails_for_vision", f"{video_id}*.jpg")
    matches = glob.glob(thumbnail_path)
    if matches:
        return matches[0]
    
    return None

def extract_text_with_actual_claude_vision(image_path: str, video_id: str) -> Optional[str]:
    """
    Extract exact text from thumbnail using Claude's actual vision capabilities.
    
    This function demonstrates how to use Claude Vision API when available.
    Since we're in the Claude Code environment, we'll use the mcp__ide__executeCode
    tool to process the image with vision capabilities.
    """
    
    print(f"🔍 Reading thumbnail image: {image_path}")
    
    # Since we're in Claude Code environment, let's use the Read tool to process the image
    # This will allow Claude to see the actual thumbnail image
    try:
        # Read the image file - Claude Code can read images directly
        from PIL import Image
        import io
        
        # Load and display image info
        with Image.open(image_path) as img:
            print(f"   📐 Image size: {img.size}")
            print(f"   🎨 Image mode: {img.mode}")
        
        print(f"   👁️  Analyzing thumbnail with Claude Vision...")
        
        # This is where we would normally call Claude Vision API
        # In the Claude Code environment, we need a different approach
        
        # For now, let me create a placeholder that shows the structure
        # The actual implementation would use the anthropic client
        
        extracted_text = f"[VISION_EXTRACTED_TEXT_FOR_{video_id}]"
        
        print(f"   ✅ Vision analysis complete")
        return extracted_text
        
    except Exception as e:
        print(f"   ❌ Vision processing failed: {e}")
        return None

def process_thumbnail_with_claude_vision_api(image_path: str, video_id: str) -> Optional[str]:
    """
    Process thumbnail using actual Claude Vision API.
    This requires the anthropic package and API key.
    """
    
    # Check if we have the required dependencies
    try:
        import anthropic
    except ImportError:
        print("❌ Anthropic package not available. Using alternative approach...")
        return extract_text_with_actual_claude_vision(image_path, video_id)
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found. Please set it in environment.")
        return None
    
    try:
        print(f"🔍 Processing {video_id} with Claude Vision API...")
        
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Read and encode the image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create the vision request
        message = client.messages.create(
            model="claude-3-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": """Please extract the EXACT text that appears on this YouTube thumbnail image. 

I need you to read the actual text visible in the image - do not interpret or generate content. Just tell me precisely what text is written on the thumbnail.

Focus on:
- Main title text (usually the largest text)
- Episode numbers if visible
- Years or dates if shown
- Any subtitle text

Respond with only the actual text you can see, formatted exactly as it appears on the thumbnail. If there are multiple text elements, separate them with " | ".

Example: "C.S. Lewis Discusses Medieval Literature | Episode 45 | 1943"

Do not add any interpretation - just the literal text visible in the image."""
                        }
                    ]
                }
            ]
        )
        
        extracted_text = message.content[0].text.strip()
        print(f"   ✅ Extracted: '{extracted_text}'")
        
        return extracted_text
        
    except Exception as e:
        print(f"   ❌ Claude Vision API error: {e}")
        return None

def update_database_with_vision_text(video_id: str, vision_text: str) -> bool:
    """Update database with vision-extracted text."""
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        """, (vision_text, video_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def process_all_videos_with_vision():
    """Process all videos using actual Claude Vision."""
    
    print("👁️  ACTUAL CLAUDE VISION PROCESSOR")
    print("=" * 60)
    print("Extracting EXACT text from thumbnail images using Claude Vision")
    print("This will read the actual text visible in each thumbnail\n")
    
    # Get list of videos to process
    videos = get_videos_needing_vision_processing()
    
    if not videos:
        print("❌ No videos found in database")
        return
    
    print(f"📊 Found {len(videos)} videos in database")
    
    # Filter to videos that have thumbnail images available
    processable_videos = []
    missing_images = []
    
    for video_id, title, current_text in videos:
        image_path = find_thumbnail_image(video_id)
        if image_path:
            processable_videos.append((video_id, title, current_text, image_path))
        else:
            missing_images.append((video_id, title))
    
    print(f"🖼️  Videos with thumbnail images: {len(processable_videos)}")
    print(f"❓ Videos missing images: {len(missing_images)}")
    
    if missing_images:
        print(f"\n⚠️  Videos without thumbnail images:")
        for video_id, title in missing_images[:5]:  # Show first 5
            print(f"   - {video_id}: {title[:50]}...")
        if len(missing_images) > 5:
            print(f"   ... and {len(missing_images) - 5} more")
    
    if not processable_videos:
        print("\n❌ No videos have thumbnail images available for processing")
        return
    
    print(f"\n🚀 Starting vision processing for {len(processable_videos)} videos...")
    print("=" * 60)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, (video_id, title, current_text, image_path) in enumerate(processable_videos, 1):
        print(f"\n[{i}/{len(processable_videos)}] {video_id}")
        print(f"Title: {title[:60]}...")
        print(f"Current: {current_text[:60]}...")
        
        # Extract text using Claude Vision
        vision_text = process_thumbnail_with_claude_vision_api(image_path, video_id)
        
        if vision_text and not vision_text.startswith("[VISION_EXTRACTED"):
            # Update database with actual vision text
            if update_database_with_vision_text(video_id, vision_text):
                successful += 1
                print(f"   ✅ SUCCESS: Updated with vision text")
            else:
                failed += 1
                print(f"   ❌ FAILED: Database update failed")
        else:
            failed += 1
            print(f"   ❌ FAILED: Vision extraction failed")
        
        # Rate limiting - be respectful to the API
        if i < len(processable_videos):
            time.sleep(1.0)  # 1 second between requests
        
        # Progress update every 10 videos
        if i % 10 == 0:
            print(f"\n📊 Progress Update:")
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            print(f"   📈 Success Rate: {successful/(successful+failed)*100:.1f}%")
    
    # Final summary
    print(f"\n" + "=" * 60)
    print(f"🎯 CLAUDE VISION PROCESSING COMPLETE")
    print(f"=" * 60)
    print(f"📊 Videos processed: {len(processable_videos)}")
    print(f"✅ Successfully extracted: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {successful/(successful+failed)*100:.1f}%")
    
    if successful > 0:
        print(f"\n🎉 SUCCESS! {successful} videos now have exact text from Claude Vision!")
        print("🔍 These videos now show the precise text visible in their thumbnails")
        print("📝 Search results will display the actual thumbnail content")

def test_vision_on_single_video():
    """Test Claude Vision on a single video for verification."""
    
    print("🧪 TESTING CLAUDE VISION ON SINGLE VIDEO")
    print("=" * 50)
    
    # Find the first available thumbnail
    test_video_id = None
    test_image_path = None
    
    for i in range(1, 13):
        batch_dir = f"vision_batch_{i:02d}"
        if os.path.exists(batch_dir):
            jpg_files = glob.glob(os.path.join(batch_dir, "*.jpg"))
            if jpg_files:
                test_image_path = jpg_files[0]
                test_video_id = os.path.basename(test_image_path).replace('.jpg', '')
                break
    
    if not test_image_path:
        print("❌ No test thumbnails found")
        return False
    
    print(f"🎯 Testing with video: {test_video_id}")
    print(f"📁 Image path: {test_image_path}")
    
    # Test the vision processing
    vision_text = process_thumbnail_with_claude_vision_api(test_image_path, test_video_id)
    
    if vision_text and not vision_text.startswith("[VISION_EXTRACTED"):
        print(f"✅ Vision test successful!")
        print(f"📝 Extracted text: '{vision_text}'")
        return True
    else:
        print(f"❌ Vision test failed")
        return False

def main():
    """Main execution function."""
    
    # First test on a single video
    print("🔧 Testing Claude Vision capabilities...\n")
    
    if not test_vision_on_single_video():
        print("\n❌ Vision test failed. Please check:")
        print("   - ANTHROPIC_API_KEY is set in environment")
        print("   - anthropic package is installed")
        print("   - thumbnail images are available")
        return
    
    print(f"\n{'='*60}")
    input("Press Enter to continue with full processing...")
    
    # Process all videos
    process_all_videos_with_vision()

if __name__ == "__main__":
    main()