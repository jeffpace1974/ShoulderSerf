#!/usr/bin/env python3
"""
Fix thumbnail text by manually setting correct values based on known patterns.
This addresses the immediate issue of incorrect thumbnail text display.
"""

import sqlite3
import sys

def fix_thumbnail_texts():
    """Fix known incorrect thumbnail texts in the database."""
    
    # Known correct thumbnail texts (based on user feedback)
    corrections = {
        # Video ID: Correct thumbnail text
        '5B4iyqPUBOE': 'C.S. Lewis Gives Tom Jones a Positive Review 1924',
        # Add more as we identify them
    }
    
    db_path = "captions.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        print("🔧 Fixing known thumbnail text errors...")
        
        # Get all videos with their current thumbnail text
        cursor = conn.execute('''
            SELECT video_id, title, thumbnail_text 
            FROM videos 
            WHERE thumbnail_text IS NOT NULL
            ORDER BY upload_date DESC
        ''')
        
        videos = cursor.fetchall()
        print(f"Found {len(videos)} videos with thumbnail text")
        
        # Apply known corrections
        fixed_count = 0
        for video_id, correct_text in corrections.items():
            result = conn.execute('''
                UPDATE videos 
                SET thumbnail_text = ? 
                WHERE video_id = ?
            ''', (correct_text, video_id))
            
            if result.rowcount > 0:
                print(f"✅ Fixed {video_id}: '{correct_text}'")
                fixed_count += 1
        
        # Clear all existing thumbnail_text to force re-extraction
        print("\n🧹 Clearing all existing thumbnail text for fresh extraction...")
        conn.execute('''
            UPDATE videos 
            SET thumbnail_text = NULL
        ''')
        
        conn.commit()
        print(f"✅ Cleared thumbnail text for all videos")
        
        # Update specific videos with correct text
        for video_id, correct_text in corrections.items():
            conn.execute('''
                UPDATE videos 
                SET thumbnail_text = ? 
                WHERE video_id = ?
            ''', (correct_text, video_id))
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Fixed {fixed_count} known incorrect entries")
        print("✅ Database updated successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🚀 Thumbnail Text Fixer")
    print("=" * 40)
    
    if fix_thumbnail_texts():
        print("\n✅ Thumbnail text corrections applied!")
        print("🔍 Search results should now show correct text for known videos")
    else:
        print("\n❌ Failed to apply corrections")

if __name__ == "__main__":
    main()