import sqlite3

# Add sample thumbnail text for testing the display
conn = sqlite3.connect('captions.db')

# Add sample text to specific videos for testing
sample_data = [
    ('EAPhFRD-nBk', 'C.S. Lewis Laughs at a Dad Joke 1924'),  # ep231 - the one you mentioned
    ('9XH-H6H_qig', 'Lewis Contemplates Oxford Academic Life 1924'),  # ep230
    ('5B4iyqPUBOE', 'C.S. Lewis Discusses Philosophy and Faith'),  # ep229
]

updated = 0
for video_id, sample_text in sample_data:
    cursor = conn.execute('''
        UPDATE videos 
        SET thumbnail_text = ? 
        WHERE video_id = ?
    ''', (sample_text, video_id))
    
    if cursor.rowcount > 0:
        print(f'✅ Added sample text to {video_id}: "{sample_text}"')
        updated += 1

conn.commit()
conn.close()

print(f'\n📊 Updated {updated} videos with sample thumbnail text')
print(f'🧪 Now search for these videos to see the thumbnail text display!')
print(f'   - Search "ep231" to see: "C.S. Lewis Laughs at a Dad Joke 1924"')
print(f'   - Search "ep230" to see: "Lewis Contemplates Oxford Academic Life 1924"')
print(f'   - Search "Dad Joke" to test thumbnail text search')