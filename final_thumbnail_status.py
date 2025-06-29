#!/usr/bin/env python3
"""
Final Thumbnail Text Status Report
Analyzes the completion and quality of thumbnail text processing across the entire database.
"""

import sqlite3
from collections import Counter, defaultdict
import re

def analyze_thumbnail_status():
    """Comprehensive analysis of thumbnail text processing status."""
    
    # Try both database files to find the correct one
    db_files = ['youtube_captions.db', 'captions.db']
    conn = None
    cursor = None
    
    for db_file in db_files:
        try:
            test_conn = sqlite3.connect(db_file)
            test_cursor = test_conn.cursor()
            test_cursor.execute("SELECT COUNT(*) FROM videos")
            video_count = test_cursor.fetchone()[0]
            if video_count > 0:
                conn = test_conn
                cursor = test_cursor
                print(f"Using database: {db_file}")
                break
            else:
                test_conn.close()
        except sqlite3.Error as e:
            if test_conn:
                test_conn.close()
            continue
    
    if not conn:
        print("ERROR: No valid database found with video data!")
        print("Checked files: " + ", ".join(db_files))
        return
    
    print("=" * 80)
    print("FINAL THUMBNAIL TEXT PROCESSING STATUS REPORT")
    print("=" * 80)
    
    # 1. Total video count
    cursor.execute("SELECT COUNT(*) FROM videos")
    total_videos = cursor.fetchone()[0]
    print(f"\n1. TOTAL VIDEOS IN DATABASE: {total_videos:,}")
    
    # 2. Videos with thumbnail text (not NULL and not empty)
    cursor.execute("""
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
        AND TRIM(thumbnail_text) != ''
    """)
    videos_with_text = cursor.fetchone()[0]
    print(f"2. VIDEOS WITH THUMBNAIL TEXT: {videos_with_text:,}")
    if total_videos > 0:
        print(f"   Coverage: {(videos_with_text/total_videos)*100:.1f}%")
    else:
        print("   Coverage: 0.0%")
    
    # 3. Videos without thumbnail text
    videos_without_text = total_videos - videos_with_text
    print(f"3. VIDEOS WITHOUT THUMBNAIL TEXT: {videos_without_text:,}")
    if total_videos > 0:
        print(f"   Missing: {(videos_without_text/total_videos)*100:.1f}%")
    else:
        print("   Missing: 0.0%")
    
    print("\n" + "="*60)
    print("THUMBNAIL TEXT QUALITY ANALYSIS")
    print("="*60)
    
    # Define generic patterns to identify
    generic_patterns = [
        'C.S. Lewis Content',
        'Daily Life', 
        'Educational Content',
        'Lewis Discussion',
        'Lewis Content',
        'Christian Content',
        'Literature Discussion',
        'Book Discussion',
        'Philosophy Discussion',
        'Theological Discussion',
        'Academic Discussion',
        'Lewis Analysis',
        'Christian Philosophy',
        'Literary Analysis'
    ]
    
    # 4. Count videos with generic patterns
    generic_count = 0
    specific_count = 0
    pattern_breakdown = Counter()
    
    cursor.execute("""
        SELECT thumbnail_text FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
        AND TRIM(thumbnail_text) != ''
    """)
    
    all_thumbnail_texts = cursor.fetchall()
    
    for (text,) in all_thumbnail_texts:
        if text:
            is_generic = False
            for pattern in generic_patterns:
                if pattern.lower() in text.lower():
                    generic_count += 1
                    pattern_breakdown[pattern] += 1
                    is_generic = True
                    break
            
            if not is_generic:
                specific_count += 1
    
    print(f"\n4. GENERIC THUMBNAIL TEXT: {generic_count:,}")
    if videos_with_text > 0:
        print(f"   Generic: {(generic_count/videos_with_text)*100:.1f}% of videos with text")
    else:
        print("   Generic: 0.0% of videos with text")
    
    print(f"\n5. SPECIFIC THUMBNAIL TEXT: {specific_count:,}")
    if videos_with_text > 0:
        print(f"   Specific: {(specific_count/videos_with_text)*100:.1f}% of videos with text")
    else:
        print("   Specific: 0.0% of videos with text")
    
    # Breakdown of generic patterns
    if generic_count > 0:
        print(f"\n   GENERIC PATTERN BREAKDOWN:")
        for pattern, count in pattern_breakdown.most_common():
            percentage = (count/generic_count)*100 if generic_count > 0 else 0
            print(f"   - '{pattern}': {count:,} videos ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("OVERALL COMPLETION STATUS")
    print("="*60)
    
    high_quality_count = specific_count
    print(f"\nHIGH QUALITY THUMBNAIL TEXT: {high_quality_count:,}")
    if total_videos > 0:
        print(f"Overall Quality Score: {(high_quality_count/total_videos)*100:.1f}%")
    else:
        print("Overall Quality Score: 0.0%")
    
    # Quality categories
    print(f"\nQUALITY BREAKDOWN:")
    if total_videos > 0:
        print(f"✅ High Quality (Specific): {high_quality_count:,} ({(high_quality_count/total_videos)*100:.1f}%)")
        print(f"⚠️  Low Quality (Generic): {generic_count:,} ({(generic_count/total_videos)*100:.1f}%)")
        print(f"❌ No Text: {videos_without_text:,} ({(videos_without_text/total_videos)*100:.1f}%)")
    else:
        print(f"✅ High Quality (Specific): {high_quality_count:,} (0.0%)")
        print(f"⚠️  Low Quality (Generic): {generic_count:,} (0.0%)")
        print(f"❌ No Text: {videos_without_text:,} (0.0%)")
    
    print("\n" + "="*60)
    print("SAMPLE HIGH-QUALITY THUMBNAIL TEXTS")
    print("="*60)
    
    # Get examples of high-quality (specific) thumbnail texts
    cursor.execute("""
        SELECT title, thumbnail_text, upload_date 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
        AND TRIM(thumbnail_text) != ''
        ORDER BY RANDOM()
        LIMIT 15
    """)
    
    examples = cursor.fetchall()
    high_quality_examples = []
    
    for title, text, upload_date in examples:
        if text:
            is_generic = False
            for pattern in generic_patterns:
                if pattern.lower() in text.lower():
                    is_generic = True
                    break
            
            if not is_generic:
                high_quality_examples.append((title, text, upload_date))
                if len(high_quality_examples) >= 10:
                    break
    
    for i, (title, text, upload_date) in enumerate(high_quality_examples, 1):
        print(f"\n{i}. TITLE: {title}")
        print(f"   THUMBNAIL: {text}")
        print(f"   DATE: {upload_date}")
    
    print("\n" + "="*60)
    print("SAMPLE GENERIC THUMBNAIL TEXTS (NEEDS IMPROVEMENT)")
    print("="*60)
    
    # Get examples of generic thumbnail texts
    cursor.execute("""
        SELECT title, thumbnail_text, upload_date 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
        AND TRIM(thumbnail_text) != ''
        ORDER BY RANDOM()
        LIMIT 20
    """)
    
    examples = cursor.fetchall()
    generic_examples = []
    
    for title, text, upload_date in examples:
        if text:
            for pattern in generic_patterns:
                if pattern.lower() in text.lower():
                    generic_examples.append((title, text, upload_date))
                    break
                    
            if len(generic_examples) >= 8:
                break
    
    for i, (title, text, upload_date) in enumerate(generic_examples, 1):
        print(f"\n{i}. TITLE: {title}")
        print(f"   THUMBNAIL: {text}")
        print(f"   DATE: {upload_date}")
    
    print("\n" + "="*60)
    print("PROCESSING RECOMMENDATIONS")
    print("="*60)
    
    if videos_without_text > 0:
        print(f"\n🔄 NEXT STEPS:")
        print(f"   - {videos_without_text:,} videos still need thumbnail text processing")
        print(f"   - Consider running vision processing on remaining videos")
    
    if generic_count > 0:
        print(f"\n🔧 QUALITY IMPROVEMENTS:")
        print(f"   - {generic_count:,} videos have generic thumbnail text")
        print(f"   - Consider re-processing with better AI prompts")
        print(f"   - Focus on videos with generic patterns for quality improvement")
    
    if high_quality_count > 0:
        print(f"\n✅ SUCCESS:")
        print(f"   - {high_quality_count:,} videos have high-quality, specific thumbnail text")
        if total_videos > 0:
            print(f"   - {(high_quality_count/total_videos)*100:.1f}% overall success rate")
        else:
            print(f"   - 0.0% overall success rate")
    
    # Close database connection
    conn.close()
    
    print("\n" + "="*80)
    print("FINAL STATUS REPORT COMPLETE")
    print("="*80)

if __name__ == "__main__":
    analyze_thumbnail_status()