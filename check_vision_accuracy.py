#!/usr/bin/env python3
"""Check accuracy of thumbnail text vs actual images"""

import sqlite3
import os
from pathlib import Path

def check_random_samples():
    conn = sqlite3.connect("captions.db") 
    cursor = conn.cursor()
    
    # Get some random videos to check
    cursor.execute("""
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 10
    """)
    
    videos = cursor.fetchall()
    
    print("🔍 CHECKING VISION ACCURACY")
    print("=" * 50)
    
    for video_id, title, thumbnail_text in videos:
        # Check if thumbnail image exists
        image_found = False
        for batch_dir in Path(".").glob("vision_batch_*"):
            image_path = batch_dir / f"{video_id}.jpg"
            if image_path.exists():
                print(f"\n📹 {video_id}")
                print(f"Title: {title}")
                print(f"Database text: {thumbnail_text}")
                print(f"Image location: {image_path}")
                image_found = True
                break
        
        if not image_found:
            print(f"\n❌ {video_id} - No image found")
    
    conn.close()

if __name__ == "__main__":
    check_random_samples()