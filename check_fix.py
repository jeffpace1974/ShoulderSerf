#!/usr/bin/env python3
"""
Check if the thumbnail text fix was applied correctly.
"""

import sqlite3

def check_fix():
    """Check the fix."""
    
    db_path = "captions.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Check the specific video that was mentioned
        cursor = conn.execute('''
            SELECT video_id, title, thumbnail_text 
            FROM videos 
            WHERE video_id = '5B4iyqPUBOE'
        ''')
        
        result = cursor.fetchone()
        if result:
            video_id, title, thumbnail_text = result
            print(f"Video: {title}")
            print(f"ID: {video_id}")
            print(f"Thumbnail Text: {thumbnail_text}")
        else:
            print("Video not found")
        
        # Also check a few other videos
        print("\nOther videos:")
        cursor = conn.execute('''
            SELECT video_id, title, thumbnail_text 
            FROM videos 
            WHERE thumbnail_text IS NOT NULL
            LIMIT 5
        ''')
        
        for video_id, title, thumbnail_text in cursor.fetchall():
            print(f"{video_id}: {thumbnail_text}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_fix()