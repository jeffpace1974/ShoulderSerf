#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 105-109
vision_extractions = [
    ("MQpQwUSjvzk", "C.S. Lewis Advertises His Atheism 1919 part 4"),
    ("MXlBKyE-zZg", "C.S. Lewis Attends an Anthroposophical Society Meeting 1924"),
    ("MaC57tUcJEQ", "1913"),
    ("My7OwOajaj0", "Dymer A Work in Progress 1922"),
    ("N7kQ4Egqlec", "C.S. Lewis Compares His Brother to God 1921"),
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