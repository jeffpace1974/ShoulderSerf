#!/usr/bin/env python3
import sqlite3

# Check what videos are in the database
conn = sqlite3.connect("captions.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM videos")
count = cursor.fetchone()[0]
print(f"Total videos in database: {count}")

cursor.execute("SELECT video_id, title, thumbnail_text FROM videos LIMIT 10")
videos = cursor.fetchall()

print("\nFirst 10 videos:")
for video in videos:
    print(f"ID: {video[0]}")
    print(f"Title: {video[1]}")
    print(f"Thumbnail text: {video[2] or 'None'}")
    print("---")

conn.close()