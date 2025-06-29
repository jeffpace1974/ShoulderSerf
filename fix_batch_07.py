#!/usr/bin/env python3
"""
Apply vision-extracted thumbnail text for batch 7 videos
All text extracted via actual vision reading of thumbnail images
"""

import sqlite3

def apply_batch_07_extractions():
    """Apply actual vision-extracted text from batch 7 thumbnails"""
    
    # Vision extractions from reading actual thumbnail images
    batch_07_extractions = {
        "WTk4k8jp0y0": "C.S. Lewis Packs Up to Move 1922",
        "WpgqciBvbxc": "C.S. Lewis Disappoints a Doctor 1923",
        "WwYCcycyjWU": "C.S. Lewis Owes His Tutor Five Pounds 1923",
        "X1tsu8p-dmI": "C.S. Lewis Disappointed with Candide 1923",
        "XXL0Yo31N9E": "C.S. Lewis Fears Being Exposed 1923",
        "XojH2PHhjAw": "C.S. Lewis Getting Medieval 1916 part 13",
        "YGJpN7ObOPM": "C.S. Lewis Meets W.B. Yeats 1921",
        "YKAIh3hvP_w": "Dymer A Work in Progress 1922",
        "YmZ0papQP2c": "C.S. Lewis Uses \"circumbendibu s\" in a Sentence 1924",
        "ZnKjI_sE2hU": "C.S. Lewis Bemused by The Fates 1922",
        "_fW2JOU1pZU": "C.S. Lewis Preparing for Publication 1918 part 6",
        "a3hlL4Vi6KY": "C.S. Lewis Has Tea with Warnie at The Red Lion 1924",
        "a4WgJTG18Pk": "C.S. Lewis Reflects on Visiting Yeats 1921",
        "a9TML0PlDs8": "a9TML0PlDs8",  # Image appears to be just a person speaking with no visible text
        "aCzbRilRVfY": "C.S. Lewis Left Disquieted and Unsettled 1924",
        "aEB0e1lP0jY": "C.S. Lewis Reflects on Death 1921",
        "aRkKG26LiK4": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
        "anwavp5B2oo": "THE COLLECTED LETTERS OF C.S.LEWIS",  # Image shows a book cover
        "b33fYNav1tU": "1915 Part 1"
    }
    
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    print("🔧 APPLYING BATCH 7 VISION EXTRACTIONS")
    print("=" * 50)
    
    updated_count = 0
    for video_id, thumbnail_text in batch_07_extractions.items():
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
    
    print(f"\n📊 BATCH 7 SUMMARY:")
    print(f"Videos updated: {updated_count}/{len(batch_07_extractions)}")
    print(f"All thumbnail text extracted via actual vision reading")
    print(f"Total batch 7 videos now have accurate thumbnail descriptions")

def verify_batch_07_updates():
    """Verify the batch 7 updates were applied correctly"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    test_videos = ["WTk4k8jp0y0", "a3hlL4Vi6KY", "b33fYNav1tU"]
    
    print(f"\n🔍 VERIFICATION OF BATCH 7 UPDATES:")
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
    apply_batch_07_extractions()
    verify_batch_07_updates()