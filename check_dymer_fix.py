#!/usr/bin/env python3
"""
Check if the Dymer fix was applied correctly.
"""

import sqlite3

def check_dymer_fix():
    """Check the Dymer fix."""
    
    db_path = "captions.db"
    conn = sqlite3.connect(db_path)
    
    # Check episode 181 specifically (from your screenshot)
    cursor = conn.execute('''
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE title LIKE '%ep181%'
    ''')
    
    result = cursor.fetchone()
    if result:
        video_id, title, thumbnail_text = result
        print("Episode 181 (from your screenshot):")
        print(f"Title: {title}")
        print(f"Thumbnail Text: {thumbnail_text}")
        print()
    
    # Check all Dymer episodes
    print("All Dymer episodes:")
    cursor = conn.execute('''
        SELECT title, thumbnail_text 
        FROM videos 
        WHERE title LIKE '%Dymer%'
        ORDER BY title
    ''')
    
    for title, thumbnail_text in cursor.fetchall():
        ep_num = title.split(' - ep')[1].split(' :')[0] if ' - ep' in title else 'unknown'
        print(f"ep{ep_num}: {thumbnail_text}")
    
    conn.close()

if __name__ == "__main__":
    check_dymer_fix()