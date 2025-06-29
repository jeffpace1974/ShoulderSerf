#!/usr/bin/env python3
"""
Check which videos have actual vision-processed thumbnail text
"""

import sqlite3

def get_vision_processed_videos():
    """Get videos that have been processed with actual vision (not generic patterns)"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Get videos with specific, non-generic thumbnail text
    cursor.execute("""
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text NOT LIKE '%Daily Life%'
        AND thumbnail_text NOT LIKE '%Content%'
        AND thumbnail_text NOT LIKE '%During the War Years%'
        AND thumbnail_text NOT LIKE '%Post-War Recovery%'
        AND thumbnail_text NOT LIKE '%University Studies%'
        AND thumbnail_text NOT LIKE '%Boxen Flashback%'
        AND LENGTH(thumbnail_text) > 10
        ORDER BY video_id
    """)
    
    vision_processed = cursor.fetchall()
    
    # Also get the manually processed ones from our sessions
    manual_vision_ids = [
        "I13FSMuY8uI", "VyiwXN2wgoQ", "6mNZLZVyfsE", "9XH-H6H_qig", 
        "ACvBFBCZaSQ", "EAPhFRD-nBk", "OTANo6PLy08", "YmZ0papQP2c",
        "a3hlL4Vi6KY", "zXgP1XBG84E", "WTk4k8jp0y0"
    ]
    
    print("🔍 VIDEOS WITH ACCURATE VISION-PROCESSED THUMBNAIL TEXT")
    print("=" * 70)
    print(f"Total videos with vision processing: {len(vision_processed)}")
    print()
    
    # Group by episode ranges for easier reading
    batch_1_videos = []
    batch_2_videos = []
    batch_3_videos = []
    other_videos = []
    
    for video_id, title, thumbnail_text in vision_processed:
        video_info = f"{video_id}: {thumbnail_text}"
        
        # Check which batch this belongs to based on video ID
        if video_id in ["-UGOdDXq4qw", "-rhF9juohqM", "09Az3PD9Kqs", "0Yzn4RYmbh4", 
                       "0dumBGcjKf8", "0kOyGUFvvZY", "0ll2gEixMuw", "1KHeBY9qymw",
                       "1teAjuEO4vQ", "24vuKBhXNaM", "2v7q_UPd0FM", "2w8pFSpTDnc",
                       "30KyLTFE77I", "3F55LrzVkbU", "3bwxgVq_c1o", "3iV-rRv7oPQ",
                       "4ICyr-4G6pk", "4pHyeEzjuPY", "52K8RL8DsPg", "5B4iyqPUBOE"]:
            batch_1_videos.append(video_info)
        elif video_id in ["5VAveRLmPrI", "5xmIDr_dPaI", "6LzINMLnu40", "6N7PV9a970k",
                         "6OP3mDXYBQk", "6WwvSCSRLAI", "6f4JRhRxbw0", "6mNZLZVyfsE",
                         "7EzpPPgBFIk", "7UbjNNetYfI", "84RnMoLdNiU", "8RZewiimr2k",
                         "8_mBexirQ8E", "8hEhsy5kXiw", "8q18l-blcSs", "9XH-H6H_qig",
                         "9wqH8eAFgj4", "9yPmfj8uEx8", "ACdyNRJf7x8", "ACvBFBCZaSQ"]:
            batch_2_videos.append(video_info)
        elif video_id in ["AjM6mmK7p7o", "Ay7zp_yaXqk", "BAZs2K5-nWM", "CMPkoeaXhBg",
                         "CePI2ByhzE4", "CqhW0YZ9KQE", "DLHdSCU7LAs", "E-M-V6_itcs",
                         "EAPhFRD-nBk", "EK1XGsWApv4", "EQkbrF9JMhA", "EiPBMwC4ODE",
                         "Er8TCF6qfd0", "F3b84bHDGf8", "FXsFyZkDUxc", "FiL9_P8QsTo",
                         "Fv2RUevPpuI", "G4PBey7JGkI", "GBdtgb5Bt0w"]:
            batch_3_videos.append(video_info)
        else:
            other_videos.append(video_info)
    
    print("📺 BATCH 1 VIDEOS (Manual Vision Processing):")
    for video in batch_1_videos[:10]:  # Show first 10
        print(f"  {video}")
    if len(batch_1_videos) > 10:
        print(f"  ... and {len(batch_1_videos) - 10} more from batch 1")
    print()
    
    print("📺 BATCH 2 VIDEOS (Vision Corrected):")
    for video in batch_2_videos[:10]:  # Show first 10
        print(f"  {video}")
    if len(batch_2_videos) > 10:
        print(f"  ... and {len(batch_2_videos) - 10} more from batch 2")
    print()
    
    print("📺 BATCH 3 VIDEOS (Vision Corrected):")
    for video in batch_3_videos[:10]:  # Show first 10
        print(f"  {video}")
    if len(batch_3_videos) > 10:
        print(f"  ... and {len(batch_3_videos) - 10} more from batch 3")
    print()
    
    if other_videos:
        print("📺 OTHER VIDEOS:")
        for video in other_videos[:5]:  # Show first 5
            print(f"  {video}")
        if len(other_videos) > 5:
            print(f"  ... and {len(other_videos) - 5} more")
    
    conn.close()
    return len(vision_processed)

def show_searchable_examples():
    """Show examples of searchable terms from vision-processed videos"""
    print("\n🔍 SEARCHABLE TERMS FROM VISION-PROCESSED VIDEOS:")
    print("=" * 60)
    
    searchable_terms = [
        ("Dad Joke", "C.S. Lewis Laughs at a Dad Joke 1924"),
        ("Tea with Warnie", "C.S. Lewis Has Tea with Warnie at The Red Lion 1924"),
        ("Insect Suffering", "C.S. Lewis Talks of Insect Suffering 1924"),
        ("Pays for His Sins", "C.S. Lewis Pays for His Sins 1924"),
        ("Packs Up to Move", "C.S. Lewis Packs Up to Move 1922"),
        ("Bach Choir", "C.S. Lewis Listens to the Bach Choir 1922"),
        ("Lawrence of Arabia", "C.S. Lewis Has Beer with Lawrence of Arabia 1922"),
        ("Socialist Sadomasochist", "C.S. Lewis The Socialist Sadomasochist 1917"),
        ("Magic Flute", "C.S. Lewis Reads Mozart's The Magic Flute 1922"),
        ("Mythbuster", "C.S. Lewis The Mythbuster 1916"),
        ("SPIRITS in Bondage", "READ ON C.S. LEWIS SPIRITS in Bondage"),
        ("Boxen Imaginary World", "Boxen: The Imaginary World of Young C. S. Lewis")
    ]
    
    for term, example in searchable_terms:
        print(f"  '{term}' → {example}")

def main():
    total_processed = get_vision_processed_videos()
    show_searchable_examples()
    
    print(f"\n📊 SUMMARY:")
    print(f"Videos with accurate vision-processed thumbnail text: {total_processed}")
    print(f"These videos will show accurate thumbnail descriptions in search results")
    print(f"Remaining videos (~{240 - total_processed}) still have generic pattern-based text")

if __name__ == "__main__":
    main()