#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 140-144
vision_extractions = [
    ("WTk4k8jp0y0", "C.S. Lewis Packs Up to Move 1922"),
    ("WpgqciBvbxc", "C.S. Lewis Disappoints a Doctor 1923"),
    ("WwYCcycyjWU", "C.S. Lewis Owes His Tutor Five Pounds 1923"),
    ("X1tsu8p-dmI", "C.S. Lewis Disappointed with Candide 1923"),
    ("XXL0Yo31N9E", "C.S. Lewis Fears Being Exposed 1923"),
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