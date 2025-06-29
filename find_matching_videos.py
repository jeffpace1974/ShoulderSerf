#!/usr/bin/env python3
import sqlite3

# Check which videos match our extracted video IDs
extracted_video_ids = [
    "I13FSMuY8uI", "VyiwXN2wgoQ", "BuM1aLdm9jM", "EYU9wLjr6tE", 
    "FkfkvNMOKSo", "i8EuVFLQxbM", "jHQD4Xczfos", "KCGMIFNjOPE",
    "wMXxOPEHtE4", "xU28TnlJOVw"
]

conn = sqlite3.connect("captions.db")
cursor = conn.cursor()

print("Looking for our extracted video IDs in database:")
for video_id in extracted_video_ids:
    cursor.execute("SELECT video_id, title, thumbnail_text FROM videos WHERE video_id = ?", (video_id,))
    result = cursor.fetchone()
    if result:
        print(f"FOUND: {result[0]} - {result[1]}")
        print(f"Current text: {result[2] or 'None'}")
        print("---")
    else:
        print(f"NOT FOUND: {video_id}")

conn.close()