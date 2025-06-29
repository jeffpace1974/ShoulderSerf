#!/usr/bin/env python3
"""
Apply vision-extracted thumbnail text for batch 4 videos
All text extracted via actual vision reading of thumbnail images
"""

import sqlite3

def apply_batch_04_extractions():
    """Apply actual vision-extracted text from batch 4 thumbnails"""
    
    # Vision extractions from reading actual thumbnail images
    batch_04_extractions = {
        "GGb_o3rlxsg": "C.S. Lewis The Mythbuster 1916 part 12",
        "GUxNweuI2S4": "C.S. Lewis The Mythbuster 1916 part 12",
        "HQo7x3l4NDc": "C.S. Lewis Reads Mozart's The Magic Flute 1922",
        "Hp-k-F4qnEM": "C.S. Lewis Under the Microscope 1922",
        "HwKsj9-qO-0": "C.S. Lewis Under the Microscope 1922",
        "I13FSMuY8uI": "C.S. Lewis Pays for His Sins 1924",
        "IWq86bZDt7g": "C.S. Lewis Reads Barfield's 'The Silver Trumpet' 1923",
        "IdIJ1FqFKBc": "C.S. Lewis Submits to Domestic Drudgery 1924",
        "IdwhZbc83W8": "1915 Part 3",
        "J5wfEDW9P48": "READ ON C.S. LEWIS SPIRITS in Bondage PART 1",
        "J7R4IxO5XPQ": "C.S. Lewis Curses His Pupil 1922",
        "JC9_JePwDj0": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
        "JEFHsl_L76g": "C.S. Lewis Rejected by the Publishers 1918 part 7",
        "JnAd4Xqe0BM": "C.S. Lewis Novice Philosopher & Freethinker 1917 part 4",
        "KDj3-pt5Wz4": "C.S. Lewis Begins His 3rd Oxford Term 1922",
        "KNa1ldT9PqQ": "C.S. Lewis Makes a Vow in Bristol with Paddy Moore 1917 part 8",
        "KRdXeqR0RY4": "C.S. Lewis Is Hypnotized 1920 part 1",
        "Kmlo5m68nms": "C.S. Lewis Gets Loud in a Library 1924",
        "KpFP-6SQFMk": "C.S. Lewis Listens to the Bach Choir 1922"
    }
    
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    print("🔧 APPLYING BATCH 4 VISION EXTRACTIONS")
    print("=" * 50)
    
    updated_count = 0
    for video_id, thumbnail_text in batch_04_extractions.items():
        # Update the thumbnail_text in the database
        cursor.execute("""
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        """, (thumbnail_text, video_id))
        
        if cursor.rowcount > 0:
            updated_count += 1
            print(f"✅ {video_id}: {thumbnail_text}")
        else:
            print(f"❌ {video_id}: NOT FOUND in database")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 BATCH 4 SUMMARY:")
    print(f"Videos updated: {updated_count}/{len(batch_04_extractions)}")
    print(f"All thumbnail text extracted via actual vision reading")
    print(f"Total batch 4 videos now have accurate thumbnail descriptions")

def verify_batch_04_updates():
    """Verify the batch 4 updates were applied correctly"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    test_videos = ["GGb_o3rlxsg", "IWq86bZDt7g", "KpFP-6SQFMk"]
    
    print(f"\n🔍 VERIFICATION OF BATCH 4 UPDATES:")
    print("=" * 50)
    
    for video_id in test_videos:
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, thumbnail_text = result
            print(f"📺 {title}")
            print(f"   Thumbnail: {thumbnail_text}")
            print()
    
    conn.close()

if __name__ == "__main__":
    apply_batch_04_extractions()
    verify_batch_04_updates()