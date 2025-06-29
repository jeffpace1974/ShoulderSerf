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

# Vision-extracted text from thumbnail images (batch 36-45)
vision_extractions = [
    ("9XH-H6H_qig", "C.S. Lewis Gives a Tom Jones a Positive Review 1924"),
    ("9wqH8eAFgj4", "C.S. Lewis Sees the Great War End 1918 part 18"),
    ("9yPmfj8uEx8", "C.S. Lewis Goes to an Interview 1922"),
    ("ACdyNRJf7x8", "C.S. Lewis Is Elected Secretary 1919 part 2"),
    ("ACvBFBCZaSQ", "C.S. Lewis Has a Bout with a Bit of Bacon 1924"),
    ("AjM6mmK7p7o", "C.S. Lewis Answered by an Illiterate 1922"),
    ("Ay7zp_yaXqk", "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 8"),
    ("BAZs2K5-nWM", "C.S. Lewis Sleeps In 1922"),
    ("CMPkoeaXhBg", "C.S. Lewis Tries to Make a Case for Pleasure 1922"),
    ("CePI2ByhzE4", "C.S. Lewis The Socialist Sadomasochist 1917 part 1"),
]

print("Updating database with vision-extracted thumbnail text (batch 36-45):")
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
print(f"🎯 Total vision-processed: 45 videos with exact thumbnail text")