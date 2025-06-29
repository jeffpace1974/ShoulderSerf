#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 61-70
vision_extractions = [
    ("G4PBey7JGkI", "C.S. Lewis Hears a Diagnosis of Lunacy 1923"),
    ("Fv2RUevPpuI", "C.S. Lewis Back to the Front 1918 part 2"),
    ("FiL9_P8QsTo", "Boxen: The Imaginary World of Young C.S. Lewis Read on C.S. Lewis flashback 1906 - 1912"),
    ("AjM6mmK7p7o", "C.S. Lewis Answered by an Illiterate 1922"),
    ("Ay7zp_yaXqk", "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 8"),
    ("BAZs2K5-nWM", "C.S. Lewis Sleeps In 1922"),
    ("CMPkoeaXhBg", "C.S. Lewis Tries to Make a Case for Pleasure 1922"),
    ("CePI2ByhzE4", "C.S. Lewis The Socialist Sadomasochist 1917 part 1"),
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