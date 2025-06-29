#!/usr/bin/env python3
"""
Apply vision-extracted thumbnail text for batch 8 videos
All text extracted via actual vision reading of thumbnail images
"""

import sqlite3

def apply_batch_08_extractions():
    """Apply actual vision-extracted text from batch 8 thumbnails"""
    
    # Vision extractions from reading actual thumbnail images
    batch_08_extractions = {
        "b6HWQZro2A8": "C.S. Lewis Hears Others' Opinions of His Aunt Lily 1924",
        "bIDCQSiqrlw": "Dymer A Work in Progress 1923",
        "bO2XBTHdK5M": "C.S. Lewis Mourns His Publisher 1920 part 6",
        "c07UgyCL_a4": "C.S. Lewis Studies John Milton 1922",
        "cfWRE6Gh3ro": "C.S. Lewis Thinks on the Meaning of Words 1922",
        "cfkiU48mUsM": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 16",
        "cpRMiyL2Zxc": "C.S. Lewis Wins at Cards 1923",
        "d3FgP42Jtiw": "C.S. Lewis The Philosopher Soldier 1917 part 9",
        "dPEeo_SPrVg": "C.S. Lewis In Misery and Depression 1922",
        "dTaUtECzrYo": "C.S. Lewis Encounters a Snake 1922",
        "dV-2MdSu0K0": "C.S. Lewis Wins the Chancellor's Prize 1921",
        "dzVBfKQGnL4": "C.S. Lewis Enjoys Hearing the Magnificat 1922",
        "e50cBLBRLvU": "C.S. Lewis Is Guilty of Loud Snoring 1922",
        "e9uJ6xZ2oyY": "1916 Part 6",
        "fJM_Z2E4FJc": "C.S. Lewis Has a Dream Come True 1922",
        "fLVLtXy9K_U": "C.S. Lewis Full of Gloomy Forebodings 1923",
        "fRYp177QTgM": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 13",
        "fijfyiq5sPU": "C.S. Lewis Full of Gloomy Forebodings 1923",
        "g9LOjTwJvOU": "C.S. Lewis Gives Aid to an Ailing Lady 1922"
    }
    
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    print("🔧 APPLYING BATCH 8 VISION EXTRACTIONS")
    print("=" * 50)
    
    updated_count = 0
    for video_id, thumbnail_text in batch_08_extractions.items():
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
    
    print(f"\n📊 BATCH 8 SUMMARY:")
    print(f"Videos updated: {updated_count}/{len(batch_08_extractions)}")
    print(f"All thumbnail text extracted via actual vision reading")
    print(f"Total batch 8 videos now have accurate thumbnail descriptions")

def verify_batch_08_updates():
    """Verify the batch 8 updates were applied correctly"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    test_videos = ["b6HWQZro2A8", "dV-2MdSu0K0", "g9LOjTwJvOU"]
    
    print(f"\n🔍 VERIFICATION OF BATCH 8 UPDATES:")
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
    apply_batch_08_extractions()
    verify_batch_08_updates()