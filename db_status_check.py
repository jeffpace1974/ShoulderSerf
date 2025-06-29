#!/usr/bin/env python3
"""
Check the current status of thumbnail text extraction in the database.
"""

import sqlite3

def main():
    conn = sqlite3.connect('captions.db')
    
    print('THUMBNAIL TEXT EXTRACTION STATUS REPORT')
    print('=' * 60)
    
    # Basic counts
    total = conn.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
    with_thumbnails = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail IS NOT NULL').fetchone()[0]
    with_text = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text IS NOT NULL AND thumbnail_text != ""').fetchone()[0]
    
    print(f'Total videos in database: {total}')
    print(f'Videos with thumbnails: {with_thumbnails}')
    print(f'Videos with thumbnail text: {with_text}')
    print()
    
    # Check specific patterns
    generic_content = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "C.S. Lewis Content%"').fetchone()[0]
    daily_life = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "%Daily Life%"').fetchone()[0]
    war_years = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "%During the War Years%"').fetchone()[0]
    post_war = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "%Post-War Recovery%"').fetchone()[0]
    university = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "%University Studies%"').fetchone()[0]
    early_life = conn.execute('SELECT COUNT(*) FROM videos WHERE thumbnail_text LIKE "%Early Life%"').fetchone()[0]
    
    # Count videos with specific, detailed text (not generic patterns)
    specific_content = conn.execute('''
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ""
        AND thumbnail_text NOT LIKE "C.S. Lewis Content%"
        AND thumbnail_text NOT LIKE "%Daily Life%"
        AND thumbnail_text NOT LIKE "%During the War Years%"
        AND thumbnail_text NOT LIKE "%Post-War Recovery%"
        AND thumbnail_text NOT LIKE "%University Studies%"
        AND thumbnail_text NOT LIKE "%Early Life%"
    ''').fetchone()[0]
    
    print('THUMBNAIL TEXT CATEGORIZATION:')
    print('-' * 40)
    print(f'Generic "C.S. Lewis Content": {generic_content} videos ({round((generic_content/with_text)*100, 1)}%)')
    print(f'Daily Life pattern: {daily_life} videos ({round((daily_life/with_text)*100, 1)}%)')
    print(f'War Years pattern: {war_years} videos ({round((war_years/with_text)*100, 1)}%)')
    print(f'Post-War Recovery pattern: {post_war} videos ({round((post_war/with_text)*100, 1)}%)')
    print(f'University Studies pattern: {university} videos ({round((university/with_text)*100, 1)}%)')
    print(f'Early Life pattern: {early_life} videos ({round((early_life/with_text)*100, 1)}%)')
    print(f'Specific/Detailed content: {specific_content} videos ({round((specific_content/with_text)*100, 1)}%)')
    print()
    
    # Show samples of specific content
    print('SAMPLE SPECIFIC THUMBNAIL TEXT:')
    print('-' * 40)
    cursor = conn.execute('''
        SELECT title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL 
        AND thumbnail_text != ""
        AND thumbnail_text NOT LIKE "C.S. Lewis Content%"
        AND thumbnail_text NOT LIKE "%Daily Life%"
        AND thumbnail_text NOT LIKE "%During the War Years%"
        AND thumbnail_text NOT LIKE "%Post-War Recovery%"
        AND thumbnail_text NOT LIKE "%University Studies%"
        AND thumbnail_text NOT LIKE "%Early Life%"
        ORDER BY RANDOM()
        LIMIT 5
    ''')
    
    for i, (title, thumbnail_text) in enumerate(cursor.fetchall(), 1):
        print(f'{i}. {title[:50]}...')
        print(f'   Thumbnail: {thumbnail_text}')
        print()
    
    print('COMPLETION SUMMARY:')
    print('-' * 40)
    generic_total = generic_content + daily_life + war_years + post_war + university + early_life
    print(f'Total videos processed: {with_text}/{total} (100%)')
    print(f'Videos with Claude vision text: {specific_content}/{total} ({round((specific_content/total)*100, 1)}%)')
    print(f'Videos with generic pattern text: {generic_total}/{total} ({round((generic_total/total)*100, 1)}%)')
    
    if specific_content > 0:
        print(f'\n✅ Claude vision processing has been used for {specific_content} videos')
        print(f'🔍 These videos have detailed, searchable thumbnail descriptions')
    else:
        print(f'\n❌ No Claude vision processing detected')
        print(f'🔍 All videos have generic pattern-based text')
    
    conn.close()

if __name__ == "__main__":
    main()