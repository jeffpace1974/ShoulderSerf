#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 86-90
vision_extractions = [
    ("I13FSMuY8uI", "C.S. Lewis Pays for His Sins 1924"),
    ("IWq86bZDt7g", "C.S. Lewis Reads Barfield's 'The Silver Trumpet' 1923"),
    ("IdIJ1FqFKBc", "C.S. Lewis Submits to Domestic Drudgery 1924"),
    ("IdwhZbc83W8", "1915 Part 3"),
    ("J5wfEDW9P48", "READ ON C.S. LEWIS SPIRITS in Bondage PART 1"),
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