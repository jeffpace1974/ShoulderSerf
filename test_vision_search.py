#!/usr/bin/env python3
"""Test search functionality with vision-extracted thumbnail text"""

import sqlite3

def test_search():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Test 1: Search for a specific phrase from vision-extracted text
    search_term = "Dad Joke"
    print(f"Searching for: '{search_term}'")
    
    cursor.execute("""
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text LIKE ? 
        ORDER BY video_id
    """, (f"%{search_term}%",))
    
    results = cursor.fetchall()
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  {result[0]} - {result[1]}")
        print(f"  Thumbnail: {result[2]}")
        print()
    
    # Test 2: Show all videos with vision-extracted text
    print("All videos with vision-extracted thumbnail text:")
    vision_video_ids = ["I13FSMuY8uI", "VyiwXN2wgoQ", "6mNZLZVyfsE", "9XH-H6H_qig", 
                       "ACvBFBCZaSQ", "EAPhFRD-nBk", "OTANo6PLy08", "YmZ0papQP2c",
                       "a3hlL4Vi6KY", "zXgP1XBG84E"]
    
    for video_id in vision_video_ids:
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        if result:
            print(f"{video_id}: {result[1]}")
    
    conn.close()

if __name__ == "__main__":
    test_search()