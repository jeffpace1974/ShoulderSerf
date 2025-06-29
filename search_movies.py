#!/usr/bin/env python3
"""
Search for movie content in the captions database.
"""

import sqlite3

def search_movies():
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Search for Luke Thompson and movie references
    print("=== Searching for Luke Thompson and movies ===")
    
    # Search for "life" + "luke" + "thompson"
    sql = """
        SELECT v.title, c.start_time, c.text, v.video_id
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE LOWER(c.text) LIKE '%life%' 
        AND LOWER(c.text) LIKE '%luke%' 
        AND LOWER(c.text) LIKE '%thompson%'
        ORDER BY v.title, CAST(c.start_time AS REAL)
        LIMIT 20
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} results for 'life' + 'luke' + 'thompson'")
    for i, row in enumerate(results):
        print(f"\n{i+1}. {row[0]}")
        print(f"   Time: {row[1]}")
        print(f"   Text: {row[2]}")
        print(f"   URL: https://youtube.com/watch?v={row[3]}&t={row[1]}")
    
    # Search for "hidden life"
    print("\n\n=== Searching for 'hidden life' ===")
    sql = """
        SELECT v.title, c.start_time, c.text, v.video_id
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE LOWER(c.text) LIKE '%hidden life%'
        ORDER BY v.title, CAST(c.start_time AS REAL)
        LIMIT 20
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} results for 'hidden life'")
    for i, row in enumerate(results):
        print(f"\n{i+1}. {row[0]}")
        print(f"   Time: {row[1]}")
        print(f"   Text: {row[2]}")
        print(f"   URL: https://youtube.com/watch?v={row[3]}&t={row[1]}")
    
    # Search for Luke Thompson more broadly
    print("\n\n=== Searching for 'Luke Thompson' ===")
    sql = """
        SELECT v.title, c.start_time, c.text, v.video_id
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE LOWER(c.text) LIKE '%luke thompson%'
        ORDER BY v.title, CAST(c.start_time AS REAL)
        LIMIT 20
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} results for 'Luke Thompson'")
    for i, row in enumerate(results):
        print(f"\n{i+1}. {row[0]}")
        print(f"   Time: {row[1]}")
        print(f"   Text: {row[2]}")
        print(f"   URL: https://youtube.com/watch?v={row[3]}&t={row[1]}")
    
    # Search for movie/film references
    print("\n\n=== Searching for 'favorite films' or 'favorite movies' ===")
    sql = """
        SELECT v.title, c.start_time, c.text, v.video_id
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE (LOWER(c.text) LIKE '%favorite film%' OR LOWER(c.text) LIKE '%favorite movie%')
        ORDER BY v.title, CAST(c.start_time AS REAL)
        LIMIT 20
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} results for 'favorite films/movies'")
    for i, row in enumerate(results):
        print(f"\n{i+1}. {row[0]}")
        print(f"   Time: {row[1]}")
        print(f"   Text: {row[2]}")
        print(f"   URL: https://youtube.com/watch?v={row[3]}&t={row[1]}")
    
    conn.close()

if __name__ == "__main__":
    search_movies()