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

# Vision-extracted text from thumbnail images
vision_extractions = [
    ("-rhF9juohqM", "1916 Part 3"),
    ("09Az3PD9Kqs", "C.S. Lewis Keeps a Diary 1922"),
    ("0Yzn4RYmbh4", "C.S. Lewis Has a Horribly Uncomfortable Dialogue 1924"),
    ("0dumBGcjKf8", "C.S. Lewis Gets Annoyed with a Friend 1922"),
    ("0kOyGUFvvZY", "C.S. Lewis Deceives His Dad 1920 part 2"),
    ("0ll2gEixMuw", "C.S. Lewis May Never Shoot the Artillery 1917 part 6"),
    ("1KHeBY9qymw", "C.S. Lewis Applies to St. John's 1924"),
    ("1teAjuEO4vQ", "C.S. Lewis Finding Some Moore Family 1917 part 5"),
    ("24vuKBhXNaM", "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912"),
    ("2v7q_UPd0FM", "C.S. Lewis Spends Time with The Philosophical Society 1924"),
    ("2w8pFSpTDnc", "C.S. Lewis Spends His Morning Painting 1923"),
    ("30KyLTFE77I", "C.S. Lewis Looks for a Summer Job 1922"),
    ("3F55LrzVkbU", "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 7"),
    ("3bwxgVq_c1o", "C.S. Lewis Has a Frankensteinian Nightmare 1923"),
    ("3iV-rRv7oPQ", "C.S. Lewis Staves Off Sickness & Madness 1923"),
    ("4ICyr-4G6pk", "C.S. Lewis Fears a Lesser Grade 1922"),
    ("4pHyeEzjuPY", "C.S. Lewis Discusses the Aim of the Artist 1923"),
    ("52K8RL8DsPg", "C.S. Lewis Son of a Freemason 1921"),
    ("5B4iyqPUBOE", "C.S. Lewis Calls on an Ancient Woman for Tea 1924"),
    ("5VAveRLmPrI", "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 2"),
    ("5xmIDr_dPaI", "The Quest of Bleheris C. S. Lewis' First Adventure Part 3 1916"),
    ("6LzINMLnu40", "C.S. Lewis Visits His Publisher 1918 part 9"),
    ("6N7PV9a970k", "C.S. Lewis Considers Owen Barfield 1921"),
    ("6OP3mDXYBQk", "C.S. Lewis Asks His Father for Funds 1921"),
]

print("Updating database with vision-extracted thumbnail text:")
print("=" * 60)

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

print(f"\n📊 Results: {successful} successful, {failed} failed")