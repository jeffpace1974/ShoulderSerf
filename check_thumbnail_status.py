import sqlite3

conn = sqlite3.connect('captions.db')

# Check current thumbnail text status
cursor = conn.execute('''
    SELECT COUNT(*) as total,
           COUNT(CASE WHEN thumbnail_text IS NOT NULL AND thumbnail_text != '' THEN 1 END) as with_text
    FROM videos 
    WHERE thumbnail IS NOT NULL
''')

result = cursor.fetchone()
total, with_text = result

print(f'Videos with thumbnails: {total}')
print(f'Videos with thumbnail text: {with_text}')

# Show sample of what we have
if with_text > 0:
    cursor = conn.execute('''
        SELECT video_id, title, thumbnail_text 
        FROM videos 
        WHERE thumbnail_text IS NOT NULL AND thumbnail_text != ''
        LIMIT 3
    ''')
    
    print(f'\nSample thumbnail text:')
    for video_id, title, text in cursor.fetchall():
        print(f'  {title[:40]}...')
        print(f'  Text: {text[:60]}...')
        print()
else:
    print('\nNo thumbnail text found - this is why it\'s not showing in search results')

conn.close()