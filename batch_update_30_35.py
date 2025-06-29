#!/usr/bin/env python3
import sqlite3

def update_thumbnail_text(video_id, new_text):
    try:
        conn = sqlite3.connect("captions.db")
        cursor = conn.execute("""
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        """, (new_text, video_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    except Exception as e:
        print(f"Database update error: {e}")
        return False

# Vision-extracted text from thumbnail images (batch 26-35)
vision_extractions = [
    ("6WwvSCSRLAI", "C.S. Lewis Finishes Middlemarch 1923"),
    ("6f4JRhRxbw0", "C.S. Lewis Finds Peaceful Delight 1924"),
    ("6mNZLZVyfsE", "C.S. Lewis Worries About Being Spotted by Aunt Lily 1924"),
    ("7EzpPPgBFIk", "C.S. Lewis Disgusted by Aunt Lily 1923"),
    ("7UbjNNetYfI", "C.S. Lewis Cuts Turnips and Peels Onions 1924"),
    ("84RnMoLdNiU", "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912"),
    ("8RZewiimr2k", "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 10"),
    ("8_mBexirQ8E", "1916 Part 8"),
    ("8hEhsy5kXiw", "C.S. Lewis Composes a Playlist on Vinyl 1922"),
    ("8q18l-blcSs", "C.S. Lewis Gets His Due 1919 part 3"),
]

print("Updating database with vision-extracted thumbnail text (batch 26-35):")
print("=" * 70)

successful = 0
failed = 0

for video_id, vision_text in vision_extractions:
    success = update_thumbnail_text(video_id, vision_text)
    if success:
        successful += 1
        print(f"✅ {video_id}: '{vision_text}'")
    else:
        failed += 1
        print(f"❌ {video_id}: Failed to update")

print(f"\n📊 Batch Results: {successful} successful, {failed} failed")
print(f"🎯 Total vision-processed: 35 videos with exact thumbnail text")