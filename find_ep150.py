#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("captions.db")
cursor = conn.cursor()

cursor.execute("SELECT video_id, title, thumbnail_text FROM videos WHERE title LIKE '%ep150%'")
result = cursor.fetchone()

if result:
    video_id, title, thumbnail_text = result
    print(f"Video ID: {video_id}")
    print(f"Title: {title}")
    print(f"Current thumbnail text: {thumbnail_text}")
else:
    print("ep150 not found")

conn.close()