#!/usr/bin/env python3
"""
Apply actual vision extractions for batch 3
"""

import sqlite3

# Actual vision extractions for batch 3 (20 videos)
batch_03_extractions = {
    "AjM6mmK7p7o": "C.S. Lewis Answered by an Illiterate 1922",  # Already fixed
    "Ay7zp_yaXqk": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 8",  # Already fixed
    "BAZs2K5-nWM": "C.S. Lewis Sleeps In 1922",  # Already fixed
    "CMPkoeaXhBg": "C.S. Lewis Tries to Make a Case for Pleasure 1922",  # Already fixed
    "CePI2ByhzE4": "C.S. Lewis The Socialist Sadomasochist 1917 part 1",  # Already fixed
    "CqhW0YZ9KQE": "C.S. Lewis Enjoys the Smell of Romance in German Fairy Tales 1923",
    "DLHdSCU7LAs": "C.S. Lewis Confounded by Editor's Ways 1922",
    "E-M-V6_itcs": "C.S. Lewis Reads the Song of Roland 1922",
    "EAPhFRD-nBk": "C.S. Lewis Dreams of Parting Ways with Mrs. Moore 1924",  # Already correct
    "EK1XGsWApv4": "C.S. Lewis Weighs Ireland's Dangers 1922",
    "EQkbrF9JMhA": "C.S. Lewis Beholds a Dressing Down 1923",
    "Ei8ZnYAVyJ8": "[No visible text - artistic image]",  # Just artistic cracked mirror image
    "EiPBMwC4ODE": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
    "Er8TCF6qfd0": "C.S. Lewis Begins His English Exams 1923",
    "F3b84bHDGf8": "C.S. Lewis Has Beer with Lawrence of Arabia 1922",
    "FXsFyZkDUxc": "Dymer A Work in Progress 1922",
    "FiL9_P8QsTo": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
    "Fv2RUevPpuI": "C.S. Lewis Back to the Front 1918 part 2",
    "G4PBey7JGkI": "C.S. Lewis Hears a Diagnosis of Lunacy 1923",
    "GBdtgb5Bt0w": "C.S. Lewis 1916 Part 10"
}

def apply_batch_03_corrections():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    updated_count = 0
    for video_id, extracted_text in batch_03_extractions.items():
        # Check if video exists and needs updating
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, current_text = result
            
            # Skip if already has correct text from previous manual fixes
            if extracted_text in current_text:
                print(f"✓ {video_id}: Already has correct text")
                continue
                
            # Skip the artistic image with no text
            if "[No visible text" in extracted_text:
                print(f"⚠️ {video_id}: Artistic image with no readable text")
                continue
                
            print(f"Updating {video_id}")
            print(f"  Title: {title}")
            print(f"  Old: {current_text}")
            print(f"  New: {extracted_text}")
            
            # Update the thumbnail text
            cursor.execute("UPDATE videos SET thumbnail_text = ? WHERE video_id = ?", 
                         (extracted_text, video_id))
            updated_count += 1
            print("  ✅ Updated")
            print()
        else:
            print(f"Video {video_id} not found in database")
    
    conn.commit()
    conn.close()
    
    print(f"\nApplied vision corrections to {updated_count} videos from batch 3")

if __name__ == "__main__":
    apply_batch_03_corrections()