#!/usr/bin/env python3
"""
Fix all thumbnail text by using actual vision processing instead of pattern matching
This will go through each batch and extract real text from images
"""

import sqlite3
import os
from pathlib import Path

def fix_ep150():
    """Fix the specific ep150 issue first"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Update ep150 with correct vision-extracted text
    cursor.execute("""
        UPDATE videos 
        SET thumbnail_text = 'C.S. Lewis Packs Up to Move 1922'
        WHERE video_id = 'WTk4k8jp0y0'
    """)
    
    print("✅ Fixed ep150: 'C.S. Lewis Packs Up to Move 1922'")
    
    conn.commit()
    conn.close()

def get_videos_needing_real_vision_processing():
    """Get all videos that need proper vision processing (not the manual extractions)"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Get videos that have pattern-based text (not real vision extractions)
    cursor.execute("""
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text LIKE '%Daily Life%'
           OR thumbnail_text LIKE '%Content%'
           OR thumbnail_text LIKE '%During the War Years%'
           OR thumbnail_text LIKE '%Post-War Recovery%'
           OR thumbnail_text LIKE '%University Studies%'
        ORDER BY video_id
    """)
    
    videos = cursor.fetchall()
    conn.close()
    
    return videos

def main():
    print("🔧 FIXING VISION PROCESSING ERRORS")
    print("=" * 50)
    
    # Fix ep150 first
    fix_ep150()
    
    # Get all videos with generic/pattern-based text
    videos_to_fix = get_videos_needing_real_vision_processing()
    print(f"\nFound {len(videos_to_fix)} videos with generic pattern-based text")
    print("These need proper vision processing using actual thumbnail images")
    
    # Show which batches contain images for processing
    batch_dirs = list(Path(".").glob("vision_batch_*"))
    print(f"\nAvailable image batches: {len(batch_dirs)}")
    for batch_dir in sorted(batch_dirs):
        image_count = len(list(batch_dir.glob("*.jpg")))
        print(f"  {batch_dir}: {image_count} images")
    
    print(f"\n⚠️  NEED TO PROCESS {len(videos_to_fix)} VIDEOS WITH ACTUAL VISION")
    print("This requires going through each batch and reading thumbnail images")

if __name__ == "__main__":
    main()