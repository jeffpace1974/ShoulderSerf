#!/usr/bin/env python3
"""
Apply vision-extracted thumbnail text to specific videos
"""

import sqlite3

# Vision-extracted text for specific video IDs
vision_extractions = {
    "I13FSMuY8uI": "C.S. Lewis Pays for His Sins 1924",  # ep220
    "VyiwXN2wgoQ": "C.S. Lewis Talks of Insect Suffering 1924",  # ep221
    "6mNZLZVyfsE": "C.S. Lewis Laughs at a Dad Joke 1924",  # ep224
    "9XH-H6H_qig": "C.S. Lewis Gives Tom Jones a Positive Review 1924",  # ep230  
    "ACvBFBCZaSQ": "C.S. Lewis Has Tea with Warnie at The Red Lion 1924",  # ep225
    "EAPhFRD-nBk": "C.S. Lewis Dreams of Parting Ways with Mrs. Moore 1924",  # ep231
    "OTANo6PLy08": "C.S. Lewis Has a Bout with a Bit of Bacon 1924",  # ep222
    "YmZ0papQP2c": "C.S. Lewis Worries About Being Spotted by Aunt Lily 1924",  # ep219
    "a3hlL4Vi6KY": "C.S. Lewis Unimpressed with Bunyan 1924",  # ep228
    "zXgP1XBG84E": "C.S. Lewis Talks of Insect Suffering 1924"  # ep226
}

def apply_vision_text():
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    updated_count = 0
    for video_id, extracted_text in vision_extractions.items():
        # Check if video exists
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, current_text = result
            print(f"Updating {video_id}")
            print(f"Title: {title}")
            print(f"Old text: {current_text or 'None'}")
            print(f"New text: {extracted_text}")
            
            # Update the thumbnail text
            cursor.execute("UPDATE videos SET thumbnail_text = ? WHERE video_id = ?", 
                         (extracted_text, video_id))
            updated_count += 1
            print("✓ Updated")
            print("---")
        else:
            print(f"Video {video_id} not found in database")
    
    conn.commit()
    conn.close()
    
    print(f"\nApplied vision-extracted text to {updated_count} videos")

if __name__ == "__main__":
    apply_vision_text()