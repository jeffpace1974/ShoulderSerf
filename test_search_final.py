#!/usr/bin/env python3
"""Test search functionality with all vision-extracted thumbnail text"""

import sqlite3

def test_comprehensive_search():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    print("🔍 COMPREHENSIVE SEARCH TESTING")
    print("=" * 50)
    
    # Test various search terms from our vision extractions
    test_searches = [
        "Dad Joke",
        "Tea with Warnie", 
        "Insect Suffering",
        "Pays for His Sins",
        "Boxen",
        "War Years",
        "Philosophy",
        "Diary",
        "University Studies",
        "Fellowship"
    ]
    
    for term in test_searches:
        # Search in thumbnail text
        cursor.execute("""
            SELECT COUNT(*) FROM videos 
            WHERE thumbnail_text LIKE ?
        """, (f"%{term}%",))
        
        count = cursor.fetchone()[0]
        print(f"'{term}': {count} videos found")
        
        if count > 0:
            # Show first result
            cursor.execute("""
                SELECT video_id, title, thumbnail_text FROM videos 
                WHERE thumbnail_text LIKE ? 
                LIMIT 1
            """, (f"%{term}%",))
            
            result = cursor.fetchone()
            if result:
                video_id, title, thumb_text = result
                print(f"  Example: {video_id} - {thumb_text}")
        print()
    
    # Test the original vision-extracted entries we know work
    print("✅ TESTING KNOWN VISION EXTRACTIONS")
    print("-" * 50)
    
    known_extractions = [
        ("I13FSMuY8uI", "Pays for His Sins"),
        ("6mNZLZVyfsE", "Dad Joke"),
        ("ACvBFBCZaSQ", "Tea with Warnie")
    ]
    
    for video_id, expected_text in known_extractions:
        cursor.execute("SELECT thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result and expected_text.lower() in result[0].lower():
            print(f"✅ {video_id}: Contains '{expected_text}'")
        else:
            print(f"❌ {video_id}: Expected '{expected_text}', got '{result[0] if result else 'None'}'")
    
    conn.close()

if __name__ == "__main__":
    test_comprehensive_search()