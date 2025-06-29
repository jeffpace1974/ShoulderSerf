#!/usr/bin/env python3
"""
Vision Text Extractor using Claude Code's image reading capabilities.

This script processes thumbnail images one by one, allowing Claude to 
read each image and extract the exact text visible.
"""

import os
import sqlite3
import glob
from pathlib import Path

def find_all_thumbnail_images():
    """Find all available thumbnail images."""
    images = []
    
    # Check vision batch directories
    for i in range(1, 13):
        batch_dir = f"vision_batch_{i:02d}"
        if os.path.exists(batch_dir):
            jpg_files = glob.glob(os.path.join(batch_dir, "*.jpg"))
            for jpg_file in jpg_files:
                video_id = os.path.basename(jpg_file).replace('.jpg', '')
                images.append((video_id, jpg_file))
    
    # Check thumbnails_for_vision directory
    if os.path.exists("thumbnails_for_vision"):
        jpg_files = glob.glob(os.path.join("thumbnails_for_vision", "*.jpg"))
        for jpg_file in jpg_files:
            filename = os.path.basename(jpg_file)
            video_id = filename.split('_')[0]  # Extract video ID from filename
            if (video_id, jpg_file) not in images:
                images.append((video_id, jpg_file))
    
    return sorted(images)

def get_video_info(video_id: str):
    """Get video information from database."""
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            SELECT title, thumbnail_text, upload_date 
            FROM videos 
            WHERE video_id = ?
        """, (video_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'title': result[0],
                'current_text': result[1] or 'No text',
                'upload_date': result[2]
            }
        else:
            return None
            
    except Exception as e:
        print(f"Database error: {e}")
        return None

def update_thumbnail_text(video_id: str, new_text: str):
    """Update thumbnail text in database."""
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        """, (new_text, video_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"Database update error: {e}")
        return False

def process_single_thumbnail(video_id: str, image_path: str):
    """Process a single thumbnail image."""
    
    print(f"\n{'='*60}")
    print(f"🎯 PROCESSING VIDEO: {video_id}")
    print(f"{'='*60}")
    
    # Get video info
    video_info = get_video_info(video_id)
    if not video_info:
        print(f"❌ Video {video_id} not found in database")
        return False
    
    print(f"📺 Title: {video_info['title']}")
    print(f"📅 Upload Date: {video_info['upload_date']}")
    print(f"📝 Current Text: {video_info['current_text']}")
    print(f"🖼️  Image: {image_path}")
    
    print(f"\n👁️  CLAUDE VISION ANALYSIS NEEDED:")
    print(f"Please examine this thumbnail image and extract the EXACT text visible:")
    
    # This is where we need manual intervention since we can't directly
    # call the Claude Vision API in this environment
    print(f"\nImage to analyze: {image_path}")
    print("Please use the Read tool to examine this image and tell me what text you see.")
    
    return True

def main():
    """Main function to start the vision text extraction process."""
    
    print("👁️  VISION TEXT EXTRACTOR")
    print("=" * 50)
    print("This script will help extract exact text from thumbnail images")
    print("using Claude's vision capabilities.\n")
    
    # Find all thumbnail images
    images = find_all_thumbnail_images()
    
    if not images:
        print("❌ No thumbnail images found")
        print("Please ensure thumbnail images are available in:")
        print("   - vision_batch_01/ through vision_batch_12/")
        print("   - thumbnails_for_vision/")
        return
    
    print(f"📊 Found {len(images)} thumbnail images")
    
    # Show first few videos that need processing
    print(f"\n🎯 Videos available for processing:")
    for i, (video_id, image_path) in enumerate(images[:10]):
        video_info = get_video_info(video_id)
        if video_info:
            title = video_info['title'][:60] + "..." if len(video_info['title']) > 60 else video_info['title']
            print(f"   {i+1:2d}. {video_id} - {title}")
    
    if len(images) > 10:
        print(f"   ... and {len(images) - 10} more videos")
    
    print(f"\n📝 INSTRUCTION:")
    print("To extract text from thumbnails, I'll show you each image.")
    print("Please examine each image and tell me the exact text you see.")
    print("This will ensure we get accurate, vision-based text extraction.")
    
    # Start with the first image as an example
    if images:
        video_id, image_path = images[0]
        process_single_thumbnail(video_id, image_path)

if __name__ == "__main__":
    main()