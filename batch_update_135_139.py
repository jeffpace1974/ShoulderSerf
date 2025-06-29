#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 135-139 (final batch from vision_batch_06)
vision_extractions = [
    ("VLS6Jddvsk0", "C.S. Lewis Becomes a Philosophy Tutor at Oxford 1924"),
    ("Vw7SO2VR1CY", "C.S. Lewis Debates a Car Ride 1920 part 4"),
    ("Vx8DsTkFaYo", "1915 Part 2"),
    ("VyiwXN2wgoQ", "C.S. Lewis Talks of Insect Suffering 1924"),
    ("W0i78r4YRuA", "C.S. Lewis Runs with Pat 1924"),
]

def update_vision_text():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'captions.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updated_count = 0
    for video_id, vision_text in vision_extractions:
        try:
            cursor.execute("""
                UPDATE videos 
                SET thumbnail_text = ? 
                WHERE video_id = ?
            """, (vision_text, video_id))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"Updated {video_id}: {vision_text}")
            else:
                print(f"Video {video_id} not found in database")
                
        except Exception as e:
            print(f"Error updating {video_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdated {updated_count} videos with vision-extracted thumbnail text")

if __name__ == "__main__":
    update_vision_text()