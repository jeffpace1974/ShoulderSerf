#!/usr/bin/env python3
"""
Fix Dymer episode thumbnail texts.
"""

import sqlite3
import re

def fix_dymer_episodes():
    """Fix Dymer-related episodes with correct thumbnail text."""
    
    db_path = "captions.db"
    conn = sqlite3.connect(db_path)
    
    # Find all Dymer episodes
    cursor = conn.execute('''
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE title LIKE '%Dymer%'
        ORDER BY title
    ''')
    
    dymer_videos = cursor.fetchall()
    print(f"Found {len(dymer_videos)} Dymer episodes to fix:")
    print("=" * 60)
    
    fixed_count = 0
    
    for video_id, title, current_text in dymer_videos:
        print(f"\nTitle: {title}")
        print(f"Current: {current_text}")
        
        # Extract year from title
        year_match = re.search(r'(\d{4})', title)
        year = year_match.group(1) if year_match else "1923"
        
        # Determine correct thumbnail text based on title content
        if "Work in Progress" in title or "A Work" in title:
            correct_text = f"Dymer - A Work in Progress {year}"
        elif "Part" in title:
            # Extract part number
            part_match = re.search(r'Part (\d+)', title)
            if part_match:
                part_num = part_match.group(1)
                correct_text = f"Dymer Part {part_num} {year}"
            else:
                correct_text = f"Dymer {year}"
        else:
            correct_text = f"Dymer {year}"
        
        print(f"Correcting to: {correct_text}")
        
        # Update the database
        conn.execute('''
            UPDATE videos 
            SET thumbnail_text = ? 
            WHERE video_id = ?
        ''', (correct_text, video_id))
        
        fixed_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Fixed {fixed_count} Dymer episodes!")
    return fixed_count

def main():
    """Main function."""
    print("🚀 Dymer Episode Thumbnail Text Fixer")
    print("=" * 60)
    
    fixed_count = fix_dymer_episodes()
    
    if fixed_count > 0:
        print(f"\n✅ Successfully corrected {fixed_count} Dymer episodes")
        print("🔍 Search results should now show correct Dymer thumbnail text")
    
if __name__ == "__main__":
    main()