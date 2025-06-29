#!/usr/bin/env python3
import sqlite3

def update_thumbnail_text(video_id, new_text):
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        """, (new_text, video_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    except Exception as e:
        print(f"Database update error: {e}")
        return False

# Update the first video with exact vision text
video_id = "-UGOdDXq4qw"
vision_text = "1916 Part 1"

success = update_thumbnail_text(video_id, vision_text)
print(f"Updated {video_id} with vision text: '{vision_text}' - Success: {success}")