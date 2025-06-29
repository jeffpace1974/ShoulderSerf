#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 91-95
vision_extractions = [
    ("J7R4IxO5XPQ", "C.S. Lewis Curses His Pupil 1922"),
    ("JC9_JePwDj0", "Boxen: The Imaginary World of Young C.S. Lewis Read on C.S. Lewis flashback 1906 - 1912"),
    ("JEFHsl_L76g", "C.S. Lewis Rejected by the Publishers 1918 part 7"),
    ("JnAd4Xqe0BM", "C.S. Lewis Novice Philosopher & Freethinker 1917 part 4"),
    ("KDj3-pt5Wz4", "C.S. Lewis Begins His 3rd Oxford Term 1922"),
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