#!/usr/bin/env python3
"""
Verify that all videos have thumbnail text processed.
"""

import sqlite3

def verify_completion():
    """Verify all thumbnails are processed."""
    
    db_path = "captions.db"
    conn = sqlite3.connect(db_path)
    
    # Get total video count
    cursor = conn.execute('SELECT COUNT(*) FROM videos')
    total_videos = cursor.fetchone()[0]
    
    # Get videos with thumbnails
    cursor = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail IS NOT NULL')
    videos_with_thumbnails = cursor.fetchone()[0]
    
    # Get videos with thumbnail text
    cursor = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text IS NOT NULL AND thumbnail_text != ""')
    videos_with_text = cursor.fetchone()[0]
    
    # Get videos still needing processing
    cursor = conn.execute('''
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail IS NOT NULL 
        AND (thumbnail_text IS NULL OR thumbnail_text = '' OR thumbnail_text = 'Text extraction requires OCR processing')
    ''')
    videos_needing_processing = cursor.fetchone()[0]
    
    print("📊 Processing Status Report")
    print("=" * 50)
    print(f"Total videos in database: {total_videos}")
    print(f"Videos with thumbnails: {videos_with_thumbnails}")
    print(f"Videos with extracted text: {videos_with_text}")
    print(f"Videos still needing processing: {videos_needing_processing}")
    print("=" * 50)
    
    if videos_needing_processing == 0:
        print("🎉 ALL VIDEOS PROCESSED!")
        print("✅ Every video with a thumbnail now has extracted text")
    else:
        print(f"⚠️  {videos_needing_processing} videos still need processing")
    
    # Show a few examples
    print("\n📝 Sample extracted texts:")
    cursor = conn.execute('''
        SELECT title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        ORDER BY RANDOM() 
        LIMIT 5
    ''')
    
    for i, (title, thumbnail_text) in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {title[:40]}...")
        print(f"   Thumbnail: {thumbnail_text}")
    
    conn.close()

if __name__ == "__main__":
    verify_completion()