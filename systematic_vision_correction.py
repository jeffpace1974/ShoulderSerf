#!/usr/bin/env python3
"""
Systematic approach to fix vision processing errors
Focus on correcting the most critical mismatches first
"""

import sqlite3

def fix_critical_vision_errors():
    """Fix the most obvious and critical vision processing errors"""
    
    # Start with ep150 and other critical fixes already identified
    critical_fixes = {
        "WTk4k8jp0y0": "C.S. Lewis Packs Up to Move 1922",  # ep150 - already fixed
        "AjM6mmK7p7o": "C.S. Lewis Answered by an Illiterate 1922",  # From batch 3
        "Ay7zp_yaXqk": "READ ON C.S. LEWIS SPIRITS in Bondage His FIRST BOOK PART 8",  # From batch 3
        "BAZs2K5-nWM": "C.S. Lewis Sleeps In 1922",  # From batch 3
        "CMPkoeaXhBg": "C.S. Lewis Tries to Make a Case for Pleasure 1922",  # From batch 3
        "CePI2ByhzE4": "C.S. Lewis The Socialist Sadomasochist 1917 part 1",  # From batch 3
        "KpFP-6SQFMk": "C.S. Lewis Listens to the Bach Choir 1922",  # From batch 4
        "w6U-iBfNvBA": "C.S. Lewis The First Metagelical? 1922",  # From batch 12
    }
    
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    updated_count = 0
    
    print("🔧 FIXING CRITICAL VISION PROCESSING ERRORS")
    print("=" * 60)
    
    for video_id, correct_text in critical_fixes.items():
        cursor.execute("SELECT title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        
        if result:
            title, current_text = result
            
            # Check if already correct
            if correct_text.lower() in current_text.lower():
                print(f"✓ {video_id}: Already correct")
                continue
                
            print(f"\n📹 {video_id}")
            print(f"Title: {title}")
            print(f"Current: {current_text}")
            print(f"Correct: {correct_text}")
            
            # Update with correct vision-extracted text
            cursor.execute("UPDATE videos SET thumbnail_text = ? WHERE video_id = ?", 
                         (correct_text, video_id))
            updated_count += 1
            print("✅ Fixed")
        else:
            print(f"❌ {video_id}: Not found in database")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 SUMMARY")
    print(f"Fixed {updated_count} critical vision processing errors")
    
    return updated_count

def analyze_remaining_errors():
    """Analyze how many videos still need proper vision processing"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    # Count videos with generic pattern-based text that need real vision processing
    cursor.execute("""
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail_text LIKE '%Daily Life%'
           OR thumbnail_text LIKE '%Content%'
           OR thumbnail_text LIKE '%During the War Years%'
           OR thumbnail_text LIKE '%Post-War Recovery%'
           OR thumbnail_text LIKE '%University Studies%'
           OR thumbnail_text LIKE '%Boxen Flashback%'
    """)
    
    remaining_generic = cursor.fetchone()[0]
    
    # Count total videos
    cursor.execute("SELECT COUNT(*) FROM videos")
    total_videos = cursor.fetchone()[0]
    
    # Count videos with proper vision text (specific, non-generic)
    cursor.execute("""
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text NOT LIKE '%Daily Life%'
        AND thumbnail_text NOT LIKE '%Content%'
        AND thumbnail_text NOT LIKE '%During the War Years%'
        AND thumbnail_text NOT LIKE '%Post-War Recovery%'
        AND thumbnail_text NOT LIKE '%University Studies%'
        AND thumbnail_text NOT LIKE '%Boxen Flashback%'
    """)
    
    properly_processed = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 VISION PROCESSING STATUS")
    print("=" * 50)
    print(f"Total videos: {total_videos}")
    print(f"Properly processed (vision): {properly_processed}")
    print(f"Still need vision processing: {remaining_generic}")
    print(f"Completion: {(properly_processed/total_videos)*100:.1f}%")
    
    return remaining_generic

def main():
    # Fix critical errors first
    fixed = fix_critical_vision_errors()
    
    # Analyze remaining work
    remaining = analyze_remaining_errors()
    
    print(f"\n🎯 NEXT STEPS")
    print("=" * 50)
    print(f"✅ Fixed {fixed} critical errors this session")
    print(f"⚠️  {remaining} videos still need proper vision processing")
    print(f"💡 Recommend processing remaining batches systematically")
    print(f"   Each batch requires reading 15-20 thumbnail images")

if __name__ == "__main__":
    main()