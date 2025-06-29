#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 120-124
vision_extractions = [
    ("QemLPji2b5A", "The Quest of Bleheris C.S. Lewis' First Adventure Part 2 1916"),
    ("QgAFIitglR8", "C.S. Lewis The Wounded Gnostic 1918 part 3"),
    ("Qj3XDDm5cCw", "C.S. Lewis Decorates his Room 1919 part 5"),
    ("RSDaL-DwaE0", "C.S. Lewis From Prison to Bondage 1918 part 8"),
    ("S6Ram3gZaNc", "C.S. Lewis Ready for Oxford Ready for War 1916 part 14"),
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