#!/usr/bin/env python3
"""
Apply vision-extracted text from batch 1 to database
"""

import sqlite3

# Vision extractions for batch 1 (20 videos)
batch_01_extractions = {
    "-UGOdDXq4qw": "C.S. Lewis 1916 Part 1",
    "-rhF9juohqM": "C.S. Lewis 1916 Part 3", 
    "09Az3PD9Kqs": "C.S. Lewis Keeps a Diary 1922",
    "0Yzn4RYmbh4": "C.S. Lewis Has a Horribly Uncomfortable Dialogue 1924",
    "0dumBGcjKf8": "C.S. Lewis Gets Annoyed with a Friend 1922",
    "0kOyGUFvvZY": "C.S. Lewis Deceives His Dad 1920 Part 2",
    "0ll2gEixMuw": "C.S. Lewis May Never Shoot the Artillery 1917 Part 6",
    "1KHeBY9qymw": "C.S. Lewis Applies to St. John's 1924",
    "1teAjuEO4vQ": "C.S. Lewis Finding Some Moore Family 1917 Part 5",
    "24vuKBhXNaM": "Boxen: The Imaginary World of Young C. S. Lewis Read on C. S. Lewis Flashback 1906 - 1912",
    "2v7q_UPd0FM": "C.S. Lewis Spends Time with The Philosophical Society 1924",
    "2w8pFSpTDnc": "C.S. Lewis Spends His Morning Painting 1923",
    "30KyLTFE77I": "C.S. Lewis Looks for a Summer Job 1922",
    "3F55LrzVkbU": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 7",
    "3bwxgVq_c1o": "C.S. Lewis Has a Frankensteinian Nightmare 1923",
    "3iV-rRv7oPQ": "C.S. Lewis Staves Off Sickness & Madness 1923",
    "4ICyr-4G6pk": "C.S. Lewis Fears a Lesser Grade 1922",
    "4pHyeEzjuPY": "C.S. Lewis Discusses the Aim of the Artist 1923",
    "52K8RL8DsPg": "C.S. Lewis Son of a Freemason 1921",
    "5B4iyqPUBOE": "C.S. Lewis Calls on an Ancient Woman for Tea 1924"
}

def apply_batch_01_extractions():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    updated_count = 0
    for video_id, extracted_text in batch_01_extractions.items():
        # Check if video exists
        cursor.execute("SELECT title FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title = result[0]
            print(f"Updating {video_id}: {extracted_text}")
            
            # Update the thumbnail text
            cursor.execute("UPDATE videos SET thumbnail_text = ? WHERE video_id = ?", 
                         (extracted_text, video_id))
            updated_count += 1
        else:
            print(f"Video {video_id} not found in database")
    
    conn.commit()
    conn.close()
    
    print(f"\nApplied vision-extracted text to {updated_count} videos from batch 1")

if __name__ == "__main__":
    apply_batch_01_extractions()