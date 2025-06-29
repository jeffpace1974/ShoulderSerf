#!/usr/bin/env python3
"""
Complete Claude Vision Processing for Remaining Videos

This script processes the remaining 83 videos that still have generic 
pattern-based thumbnail text, using Claude's vision capabilities to 
extract accurate text from their thumbnail images.
"""

import os
import sys
import sqlite3
import base64
from pathlib import Path
import time
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import anthropic
except ImportError:
    print("❌ Anthropic package not found. Install with: pip install anthropic")
    sys.exit(1)

class ClaudeVisionProcessor:
    """Process thumbnails using Claude's vision capabilities."""
    
    def __init__(self, db_path: str = "captions.db"):
        self.db_path = db_path
        self.client = self._initialize_claude_client()
        self.vision_batch_dirs = [
            f"vision_batch_{i:02d}" for i in range(1, 13)
        ]
        
    def _initialize_claude_client(self):
        """Initialize Claude client with API key."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in environment variables")
            print("   Please set your Claude API key in .env file")
            sys.exit(1)
        
        return anthropic.Anthropic(api_key=api_key)
    
    def load_videos_to_process(self) -> List[str]:
        """Load list of video IDs that need processing."""
        video_list_file = "claude_vision_ready_list.txt"
        
        if not os.path.exists(video_list_file):
            print(f"❌ {video_list_file} not found")
            print("   Run the analysis script first to generate the list")
            return []
        
        video_ids = []
        with open(video_list_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('Video') and not line.startswith('='):
                    video_ids.append(line)
        
        print(f"📋 Loaded {len(video_ids)} videos to process")
        return video_ids
    
    def find_thumbnail_image(self, video_id: str) -> Optional[str]:
        """Find the thumbnail image for a given video ID."""
        for batch_dir in self.vision_batch_dirs:
            if os.path.exists(batch_dir):
                thumbnail_path = os.path.join(batch_dir, f"{video_id}.jpg")
                if os.path.exists(thumbnail_path):
                    return thumbnail_path
        
        print(f"⚠️  Thumbnail not found for {video_id}")
        return None
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for Claude Vision API."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_with_claude_vision(self, image_path: str, video_id: str) -> Optional[str]:
        """Extract text from thumbnail using Claude Vision."""
        try:
            print(f"🔍 Processing thumbnail for {video_id}")
            
            # Encode image
            image_base64 = self.encode_image_to_base64(image_path)
            
            # Create message for Claude
            message = self.client.messages.create(
                model="claude-3-sonnet-20241022",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": """This is a YouTube thumbnail for a C.S. Lewis content video. Please extract the exact text that appears on this thumbnail. 

Focus on:
1. The main title text (usually large and prominent)
2. Any episode numbers or dates
3. Any descriptive text about the content
4. Book titles or specific topics mentioned

Please provide ONLY the text that appears on the thumbnail, formatted as it appears. Do not add interpretation or context - just the exact text visible in the image.

If there are multiple text elements, separate them with " | " (space pipe space).

Example format: "C.S. Lewis Discusses Medieval Literature | Episode 45 | 1943" """
                            }
                        ]
                    }
                ]
            )
            
            extracted_text = message.content[0].text.strip()
            print(f"✅ Extracted: '{extracted_text}'")
            return extracted_text
            
        except Exception as e:
            print(f"❌ Error processing {video_id}: {e}")
            return None
    
    def update_database(self, video_id: str, new_thumbnail_text: str) -> bool:
        """Update the database with new thumbnail text."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update thumbnail_text for the video
            cursor.execute("""
                UPDATE videos 
                SET thumbnail_text = ? 
                WHERE video_id = ?
            """, (new_thumbnail_text, video_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"💾 Database updated for {video_id}")
                conn.close()
                return True
            else:
                print(f"⚠️  No video found in database with ID: {video_id}")
                conn.close()
                return False
                
        except Exception as e:
            print(f"❌ Database error for {video_id}: {e}")
            return False
    
    def get_current_thumbnail_text(self, video_id: str) -> str:
        """Get current thumbnail text from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT thumbnail_text 
                FROM videos 
                WHERE video_id = ?
            """, (video_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0] or "No thumbnail text"
            else:
                return "Video not found"
                
        except Exception as e:
            print(f"❌ Error getting current text for {video_id}: {e}")
            return "Error"
    
    def process_single_video(self, video_id: str) -> bool:
        """Process a single video's thumbnail."""
        print(f"\n🎯 Processing Video: {video_id}")
        print("-" * 50)
        
        # Get current thumbnail text
        current_text = self.get_current_thumbnail_text(video_id)
        print(f"Current text: '{current_text}'")
        
        # Skip if already has good text (not generic pattern)
        generic_patterns = [
            "C.S. Lewis Content",
            "Daily Life",
            "During the War Years",
            "Post-War Recovery",
            "University Studies",
            "Dymer A Work in Progress"
        ]
        
        if not any(pattern in current_text for pattern in generic_patterns):
            print(f"✅ Video {video_id} already has good thumbnail text, skipping")
            return True
        
        # Find thumbnail image
        thumbnail_path = self.find_thumbnail_image(video_id)
        if not thumbnail_path:
            return False
        
        # Extract text with Claude Vision
        extracted_text = self.extract_text_with_claude_vision(thumbnail_path, video_id)
        if not extracted_text:
            return False
        
        # Update database
        success = self.update_database(video_id, extracted_text)
        
        if success:
            print(f"🎉 Successfully processed {video_id}")
            print(f"   Old: '{current_text}'")
            print(f"   New: '{extracted_text}'")
        
        return success
    
    def process_all_videos(self, batch_size: int = 10, delay: float = 2.0):
        """Process all videos in the list."""
        video_ids = self.load_videos_to_process()
        if not video_ids:
            return
        
        print(f"\n🚀 Starting Claude Vision Processing")
        print(f"📊 Total videos to process: {len(video_ids)}")
        print(f"⚙️  Batch size: {batch_size}")
        print(f"⏱️  Delay between requests: {delay} seconds")
        print("=" * 60)
        
        success_count = 0
        failed_count = 0
        
        for i, video_id in enumerate(video_ids, 1):
            print(f"\n📍 Progress: {i}/{len(video_ids)}")
            
            success = self.process_single_video(video_id)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # Rate limiting delay
            if i < len(video_ids):  # Don't delay after last item
                print(f"⏸️  Waiting {delay} seconds...")
                time.sleep(delay)
            
            # Batch status update
            if i % batch_size == 0:
                print(f"\n📊 Batch {i//batch_size} Complete:")
                print(f"   ✅ Successful: {success_count}")
                print(f"   ❌ Failed: {failed_count}")
                print(f"   📈 Success Rate: {success_count/(success_count+failed_count)*100:.1f}%")
        
        # Final summary
        print(f"\n" + "=" * 60)
        print(f"🎯 CLAUDE VISION PROCESSING COMPLETE")
        print(f"=" * 60)
        print(f"✅ Successfully processed: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📈 Overall success rate: {success_count/(success_count+failed_count)*100:.1f}%")
        
        if success_count > 0:
            print(f"\n🎉 Great! {success_count} videos now have accurate Claude vision-extracted thumbnail text!")
            print("🔍 You can now search for specific terms in these thumbnails")


def main():
    """Main execution function."""
    print("🤖 Claude Vision Thumbnail Text Processor")
    print("=" * 50)
    print("This will process remaining videos with generic thumbnail text")
    print("using Claude's vision capabilities for accurate text extraction.\n")
    
    # Initialize processor
    processor = ClaudeVisionProcessor()
    
    # Process all videos
    processor.process_all_videos(batch_size=10, delay=2.0)


if __name__ == "__main__":
    main()