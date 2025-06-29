#!/usr/bin/env python3
"""
Show videos with generic thumbnail text that need improvement.
"""

import sqlite3

def show_generic_videos():
    """Show specific videos that still have generic thumbnail text."""
    
    # Connect to database
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Define generic patterns
    generic_patterns = [
        'C.S. Lewis Content',
        'Daily Life', 
        'Educational Content',
        'Lewis Discussion',
        'Lewis Content',
        'Christian Content',
        'Literature Discussion',
        'Book Discussion',
        'Philosophy Discussion',
        'Theological Discussion',
        'Academic Discussion',
        'Lewis Analysis',
        'Christian Philosophy',
        'Literary Analysis'
    ]
    
    print("VIDEOS WITH GENERIC THUMBNAIL TEXT")
    print("=" * 60)
    
    # Get all videos with thumbnail text
    cursor.execute("""
        SELECT video_id, title, thumbnail_text, upload_date 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
        AND TRIM(thumbnail_text) != ''
        ORDER BY upload_date DESC
    """)
    
    all_videos = cursor.fetchall()
    generic_videos = []
    
    for video_id, title, text, upload_date in all_videos:
        if text:
            for pattern in generic_patterns:
                if pattern.lower() in text.lower():
                    generic_videos.append((video_id, title, text, upload_date))
                    break
    
    if generic_videos:
        for i, (video_id, title, text, upload_date) in enumerate(generic_videos, 1):
            print(f"\n{i}. VIDEO ID: {video_id}")
            print(f"   TITLE: {title}")
            print(f"   THUMBNAIL: {text}")
            print(f"   DATE: {upload_date}")
            print(f"   URL: https://youtube.com/watch?v={video_id}")
    else:
        print("\nNo videos found with generic thumbnail text!")
    
    print(f"\nTOTAL GENERIC VIDEOS: {len(generic_videos)}")
    
    conn.close()

if __name__ == "__main__":
    show_generic_videos()