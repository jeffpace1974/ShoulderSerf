#!/usr/bin/env python3
"""
Apply vision-extracted thumbnail text for batch 5 videos
All text extracted via actual vision reading of thumbnail images
"""

import sqlite3

def apply_batch_05_extractions():
    """Apply actual vision-extracted text from batch 5 thumbnails"""
    
    # Vision extractions from reading actual thumbnail images
    batch_05_extractions = {
        "L-3y3x0Wcho": "C.S. Lewis Theatre Critic 1922",
        "L4sp1hLkMfg": "The Quest of Bleheris C. S. Lewis' First Adventure Part 1 1916",
        "L5rkwXkkY9o": "C.S. Lewis Visits His Aunt Lily 1922",
        "LuWLSXbEU5c": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 5",
        "MIUhf4XZfF0": "C.S. Lewis Attacks His Father 1919 part 7",
        "MQpQwUSjvzk": "C.S. Lewis Advertises His Atheism 1919 part 4",
        "MXlBKyE-zZg": "C.S. Lewis Attends an Anthroposophical Society Meeting 1924",
        "MaC57tUcJEQ": "1913",
        "My7OwOajaj0": "Dymer A Work in Progress 1922",
        "N7kQ4Egqlec": "C.S. Lewis Compares His Brother to God 1921",
        "NXQV6t3qWeo": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
        "NmLU-B7ismI": "C.S. Lewis Considers Cornell University 1922",
        "O7uJtBnjbwE": "Dymer A Work in Progress 1922",
        "OHIpma3urTU": "C.S. Lewis Is Startled by Pheasants 1922",
        "OTANo6PLy08": "C.S. Lewis Unimpressed with Bunyan 1924",
        "OY4wuhqIjX0": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 6",
        "Po4CglYYLJA": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 15",
        "PsvA4VCySHI": "C.S. Lewis Takes Note of Nude Bodies 1922",
        "QEY8DfEu-Lw": "C.S. Lewis Goes Out for Cigarettes 1922",
        "QRc_GNnWPAg": "C.S. Lewis Has Exclusive Discussions 1923"
    }
    
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    print("🔧 APPLYING BATCH 5 VISION EXTRACTIONS")
    print("=" * 50)
    
    updated_count = 0
    for video_id, thumbnail_text in batch_05_extractions.items():
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
    
    print(f"\n📊 BATCH 5 SUMMARY:")
    print(f"Videos updated: {updated_count}/{len(batch_05_extractions)}")
    print(f"All thumbnail text extracted via actual vision reading")
    print(f"Total batch 5 videos now have accurate thumbnail descriptions")

def verify_batch_05_updates():
    """Verify the batch 5 updates were applied correctly"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    test_videos = ["L-3y3x0Wcho", "LuWLSXbEU5c", "QRc_GNnWPAg"]
    
    print(f"\n🔍 VERIFICATION OF BATCH 5 UPDATES:")
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
    apply_batch_05_extractions()
    verify_batch_05_updates()