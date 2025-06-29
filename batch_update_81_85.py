#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 81-85
vision_extractions = [
    ("GGb_o3rlxsg", "Castle/tower artwork - no text visible"),
    ("GUxNweuI2S4", "C.S. Lewis The Mythbuster 1916 part 12"),
    ("HQo7x3l4NDc", "C.S. Lewis Reads Mozart's The Magic Flute 1922"),
    ("Hp-k-F4qnEM", "C.S. Lewis Under the Microscope 1922"),
    ("HwKsj9-qO-0", "Dymer A Work in Progress 1922"),
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