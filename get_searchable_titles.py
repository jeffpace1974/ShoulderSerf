#!/usr/bin/env python3
"""
Get the actual video titles for vision-processed videos so user can search on the website
"""

import sqlite3

def get_searchable_video_titles():
    """Get video titles for vision-processed videos that can be searched on the website"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Get specific videos with known good vision processing
    known_vision_videos = [
        "6mNZLZVyfsE",  # Dad Joke
        "ACvBFBCZaSQ",  # Tea with Warnie  
        "WTk4k8jp0y0",  # Packs Up to Move (ep150)
        "KpFP-6SQFMk",  # Bach Choir
        "F3b84bHDGf8",  # Lawrence of Arabia
        "CePI2ByhzE4",  # Socialist Sadomasochist
        "GUxNweuI2S4",  # Mythbuster
        "I13FSMuY8uI",  # Pays for His Sins
        "VyiwXN2wgoQ",  # Insect Suffering
        "HQo7x3l4NDc",  # Magic Flute
        "5VAveRLmPrI",  # SPIRITS in Bondage
        "24vuKBhXNaM",  # Boxen
    ]
    
    print("🔍 SEARCHABLE VIDEOS ON THE 5001 WEBSITE")
    print("=" * 60)
    print("These videos have accurate vision-processed thumbnail text:")
    print()
    
    for video_id in known_vision_videos:
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, thumbnail_text = result
            print(f"📺 **{title}**")
            print(f"   Thumbnail text: {thumbnail_text}")
            print(f"   Search term: Extract key words from thumbnail text")
            print()
    
    # Also get some additional ones from recent processing
    cursor.execute("""
        SELECT title, thumbnail_text FROM videos 
        WHERE thumbnail_text LIKE '%Dad Joke%' 
           OR thumbnail_text LIKE '%Tea with Warnie%'
           OR thumbnail_text LIKE '%Packs Up%'
           OR thumbnail_text LIKE '%Bach Choir%'
           OR thumbnail_text LIKE '%Lawrence of Arabia%'
           OR thumbnail_text LIKE '%Socialist%'
           OR thumbnail_text LIKE '%Mythbuster%'
           OR thumbnail_text LIKE '%SPIRITS in Bondage%'
           OR thumbnail_text LIKE '%Boxen%'
        ORDER BY title
    """)
    
    additional_results = cursor.fetchall()
    
    print("🎯 RECOMMENDED SEARCH TESTS:")
    print("=" * 40)
    print("Try searching these terms on localhost:5001:")
    print()
    print("• 'Dad Joke' - should find ep224")
    print("• 'Tea with Warnie' - should find ep225") 
    print("• 'Packs Up' - should find ep150")
    print("• 'Bach Choir' - should find ep166")
    print("• 'Lawrence of Arabia' - should find ep145")
    print("• 'Socialist' - should find ep38")
    print("• 'Mythbuster' - should find ep35")
    print("• 'SPIRITS' - should find multiple Spirits in Bondage episodes")
    print("• 'Boxen' - should find multiple Boxen flashback episodes")
    
    conn.close()

if __name__ == "__main__":
    get_searchable_video_titles()