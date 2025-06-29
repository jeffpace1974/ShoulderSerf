#!/usr/bin/env python3

import sqlite3
import os

# Vision-extracted text from thumbnails 125-129
vision_extractions = [
    ("SO7UxoiPOAY", "Post-apocalyptic cityscape framed view - no text"),
    ("ShCu7khyhzA", "C.S. Lewis Hosts a Good Friday Guest 1924"),
    ("SukyoIZW1zo", "C.S. Lewis Considers Visiting Yeats 1919 part 8"),
    ("T7A0eXsb-dc", "C.S. Lewis Recalls Spenser and Milton 1920 part 5"),
    ("UJO0M2LSwpg", "1914 Part 2"),
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