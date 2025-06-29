import sqlite3

# Clear the incorrect thumbnail text data
conn = sqlite3.connect('captions.db')

# Remove all the fake thumbnail text I generated
conn.execute('''
    UPDATE videos 
    SET thumbnail_text = NULL 
    WHERE thumbnail_text LIKE 'Read on C.S. Lewis ep%'
    OR thumbnail_text LIKE 'Read on C.S. Lewis Episode%'
    OR thumbnail_text = 'Read on C.S. Lewis Episode'
''')

# Check what real OCR text we have
cursor = conn.execute('''
    SELECT COUNT(*) 
    FROM videos 
    WHERE thumbnail_text IS NOT NULL 
    AND thumbnail_text != ''
''')

remaining_real = cursor.fetchone()[0]

conn.commit()
conn.close()

print(f'✅ Cleared incorrect thumbnail text')
print(f'📊 Real OCR text remaining: {remaining_real} videos')
print(f'🎯 Status: System cleaned up, ready for proper OCR solution')