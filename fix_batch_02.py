#!/usr/bin/env python3
"""
Apply actual vision extractions for batch 2
"""

import sqlite3

# Actual vision extractions for batch 2 (20 videos)
batch_02_extractions = {
    "5VAveRLmPrI": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 2",
    "5xmIDr_dPaI": "The Quest of Bleheris C. S. Lewis' First Adventure Part 3 1916",
    "6LzINMLnu40": "C.S. Lewis Visits His Publisher 1918 part 9",
    "6N7PV9a970k": "C.S. Lewis Considers Owen Barfield 1921",
    "6OP3mDXYBQk": "C.S. Lewis Asks His Father for Funds 1921",
    "6WwvSCSRLAI": "C.S. Lewis Finishes Middlemarch 1923",
    "6f4JRhRxbw0": "C.S. Lewis Finds Peaceful Delight 1924",
    "6mNZLZVyfsE": "C.S. Lewis Laughs at a Dad Joke 1924",  # Already correct from previous fix
    "7EzpPPgBFIk": "C.S. Lewis Disgusted by Aunt Lily 1923",
    "7UbjNNetYfI": "C.S. Lewis Cuts Turnips and Peels Onions 1924",
    "84RnMoLdNiU": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis flashback 1906 - 1912",
    "8RZewiimr2k": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 10", 
    "8_mBexirQ8E": "C.S. Lewis 1916 Part 8",
    "8hEhsy5kXiw": "C.S. Lewis Composes a Playlist on Vinyl 1922",
    "8q18l-blcSs": "C.S. Lewis Gets His Due 1919 part 3",
    "9XH-H6H_qig": "C.S. Lewis Gives Tom Jones a Positive Review 1924",  # Already correct from previous fix
    "9wqH8eAFgj4": "C.S. Lewis Sees the Great War End 1918 part 10",
    "9yPmfj8uEx8": "C.S. Lewis Goes to an Interview 1922",
    "ACdyNRJf7x8": "C.S. Lewis Is Elected Secretary 1919 part 2",
    "ACvBFBCZaSQ": "C.S. Lewis Has Tea with Warnie at The Red Lion 1924"  # Already correct from previous fix
}

def apply_batch_02_corrections():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    updated_count = 0
    for video_id, extracted_text in batch_02_extractions.items():
        # Check if video exists and needs updating
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, current_text = result
            
            # Skip if already has correct text from previous manual fixes
            if video_id in ["6mNZLZVyfsE", "9XH-H6H_qig", "ACvBFBCZaSQ"] and "C.S. Lewis" in current_text:
                print(f"✓ {video_id}: Already has correct text")
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
    
    print(f"\nApplied vision corrections to {updated_count} videos from batch 2")

if __name__ == "__main__":
    apply_batch_02_corrections()