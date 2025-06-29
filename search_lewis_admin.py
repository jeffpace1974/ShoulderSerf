#!/usr/bin/env python3
"""
Search for Lewis discussing administrative positions and concerns about being authoritarian.
"""

import sqlite3
import re
from typing import List, Tuple

def connect_to_db(db_path: str = "captions.db"):
    """Connect to the captions database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def search_administrative_content(conn: sqlite3.Connection) -> List[Tuple]:
    """
    Search for content about Lewis and administrative positions.
    """
    # Administrative position keywords
    admin_terms = [
        "president", "vice president", "dean", "principal", "vice principal", 
        "administrator", "administrative", "master", "head", "director"
    ]
    
    # Authority/character concern keywords
    authority_terms = [
        "authoritarian", "harsh", "discipline", "authority", "firm", "strict",
        "hard", "tough", "demanding", "severe", "rigid", "inflexible"
    ]
    
    # Personal trait keywords Lewis might use
    personal_terms = [
        "wouldn't be good", "not suited", "not cut out", "couldn't", "unable",
        "too soft", "too kind", "too gentle", "weakness", "character", "nature",
        "personality", "temperament"
    ]
    
    results = []
    
    # First, let's see the table structure
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='caption_segments';")
    schema = cursor.fetchone()
    if schema:
        print("Table schema:")
        print(schema[0])
        print("\n" + "="*50 + "\n")
    
    # Check if we have FTS5 search available
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name LIKE '%fts%';")
    fts_tables = cursor.fetchall()
    
    has_fts = False
    for table in fts_tables:
        if table and 'caption_segments' in str(table[0]):
            has_fts = True
            print(f"Found FTS table: {table[0]}")
            break
    
    print(f"FTS5 available: {has_fts}\n")
    
    # Get sample data to understand structure
    cursor.execute("SELECT * FROM caption_segments LIMIT 3;")
    sample_rows = cursor.fetchall()
    if sample_rows:
        print("Sample data structure:")
        for i, row in enumerate(sample_rows):
            print(f"Row {i+1}: {dict(row)}")
        print("\n" + "="*50 + "\n")
    
    # Strategy 1: Search for administrative terms in episodes < 232
    admin_pattern = "|".join(admin_terms)
    
    query1 = """
    SELECT DISTINCT v.episode_number, cs.start_time, cs.end_time, cs.text, v.title
    FROM caption_segments cs
    JOIN videos v ON cs.video_id = v.id
    WHERE v.episode_number < 232 
    AND v.episode_number IS NOT NULL
    AND (cs.text LIKE '%president%' OR cs.text LIKE '%dean%' OR cs.text LIKE '%principal%' 
         OR cs.text LIKE '%administrator%' OR cs.text LIKE '%administrative%'
         OR cs.text LIKE '%master%' OR cs.text LIKE '%head%' OR cs.text LIKE '%director%')
    ORDER BY v.episode_number, cs.start_time;
    """
    
    print("Searching for administrative position mentions...")
    cursor.execute(query1)
    admin_results = cursor.fetchall()
    
    print(f"Found {len(admin_results)} segments mentioning administrative positions\n")
    
    # Strategy 2: Search for authority/character concerns
    query2 = """
    SELECT DISTINCT v.episode_number, cs.start_time, cs.end_time, cs.text, v.title
    FROM caption_segments cs
    JOIN videos v ON cs.video_id = v.id
    WHERE v.episode_number < 232 
    AND v.episode_number IS NOT NULL
    AND (cs.text LIKE '%authoritarian%' OR cs.text LIKE '%harsh%' OR cs.text LIKE '%discipline%'
         OR cs.text LIKE '%authority%' OR cs.text LIKE '%firm%' OR cs.text LIKE '%strict%'
         OR cs.text LIKE '%wouldn''t be good%' OR cs.text LIKE '%not suited%'
         OR cs.text LIKE '%too soft%' OR cs.text LIKE '%too kind%' OR cs.text LIKE '%character%')
    ORDER BY v.episode_number, cs.start_time;
    """
    
    print("Searching for authority/character concern mentions...")
    cursor.execute(query2)
    authority_results = cursor.fetchall()
    
    print(f"Found {len(authority_results)} segments mentioning authority/character concerns\n")
    
    # Strategy 3: Combined search for both concepts
    query3 = """
    SELECT DISTINCT v.episode_number, cs.start_time, cs.end_time, cs.text, v.title
    FROM caption_segments cs
    JOIN videos v ON cs.video_id = v.id
    WHERE v.episode_number < 232 
    AND v.episode_number IS NOT NULL
    AND (
        (cs.text LIKE '%president%' OR cs.text LIKE '%dean%' OR cs.text LIKE '%principal%' 
         OR cs.text LIKE '%administrator%' OR cs.text LIKE '%administrative%')
        AND 
        (cs.text LIKE '%authoritarian%' OR cs.text LIKE '%harsh%' OR cs.text LIKE '%authority%'
         OR cs.text LIKE '%wouldn''t%' OR cs.text LIKE '%couldn''t%' OR cs.text LIKE '%not suited%'
         OR cs.text LIKE '%too%' OR cs.text LIKE '%character%' OR cs.text LIKE '%nature%')
    )
    ORDER BY v.episode_number, cs.start_time;
    """
    
    print("Searching for segments containing BOTH administrative and character concepts...")
    cursor.execute(query3)
    combined_results = cursor.fetchall()
    
    print(f"Found {len(combined_results)} segments with both concepts\n")
    
    # Return all unique results
    all_results = []
    seen = set()
    
    for result_set in [admin_results, authority_results, combined_results]:
        for row in result_set:
            key = (row['episode_number'], row['start_time'], row['text'])
            if key not in seen:
                seen.add(key)
                all_results.append(row)
    
    return all_results

def format_timestamp(seconds):
    """Convert seconds to MM:SS format."""
    if seconds is None:
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def main():
    conn = connect_to_db()
    if not conn:
        print("Could not connect to database")
        return
    
    try:
        results = search_administrative_content(conn)
        
        if not results:
            print("No results found.")
            return
        
        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS: {len(results)} segments found")
        print(f"{'='*80}\n")
        
        current_episode = None
        for row in sorted(results, key=lambda x: (x['episode_number'] or 0, x['start_time'] or 0)):
            if current_episode != row['episode_number']:
                current_episode = row['episode_number']
                print(f"\n{'─'*60}")
                print(f"EPISODE {current_episode}: {row['title']}")
                print(f"{'─'*60}")
            
            start_time = format_timestamp(row['start_time'])
            end_time = format_timestamp(row['end_time'])
            
            print(f"\nTimestamp: {start_time} - {end_time}")
            print(f"Text: {row['text']}")
            print()
        
        # Also search for specific phrases that might be relevant
        print(f"\n{'='*80}")
        print("ADDITIONAL TARGETED SEARCH")
        print(f"{'='*80}\n")
        
        targeted_queries = [
            ("offered position", "cs.text LIKE '%offered%' AND (cs.text LIKE '%position%' OR cs.text LIKE '%job%')"),
            ("declined role", "cs.text LIKE '%declined%' OR cs.text LIKE '%turned down%' OR cs.text LIKE '%refused%'"),
            ("college position", "cs.text LIKE '%college%' AND (cs.text LIKE '%position%' OR cs.text LIKE '%role%')"),
            ("oxford admin", "cs.text LIKE '%oxford%' AND (cs.text LIKE '%admin%' OR cs.text LIKE '%master%' OR cs.text LIKE '%head%')"),
            ("cambridge admin", "cs.text LIKE '%cambridge%' AND (cs.text LIKE '%admin%' OR cs.text LIKE '%master%' OR cs.text LIKE '%head%')")
        ]
        
        cursor = conn.cursor()
        for search_name, condition in targeted_queries:
            query = f"""
            SELECT DISTINCT v.episode_number, cs.start_time, cs.end_time, cs.text, v.title
            FROM caption_segments cs
            JOIN videos v ON cs.video_id = v.id
            WHERE v.episode_number < 232 
            AND v.episode_number IS NOT NULL
            AND {condition}
            ORDER BY v.episode_number, cs.start_time;
            """
            
            cursor.execute(query)
            targeted_results = cursor.fetchall()
            
            if targeted_results:
                print(f"\n{search_name.upper()}: {len(targeted_results)} results")
                print("-" * 40)
                for row in targeted_results:
                    start_time = format_timestamp(row['start_time'])
                    print(f"Episode {row['episode_number']} at {start_time}: {row['text'][:200]}...")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()