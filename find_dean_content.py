#!/usr/bin/env python3
"""
Search specifically for the Dean-related content.
"""

import sqlite3
import re

def connect_to_db(db_path: str = "captions.db"):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def extract_episode_number(title: str) -> int:
    patterns = [
        r'Episode (\d+)',
        r'Ep\.? (\d+)',
        r'#(\d+)',
        r'Part (\d+)',
        r'(\d+)\s*-',
        r'^\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0

def format_timestamp(time_str):
    if not time_str:
        return "N/A"
    
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{int(seconds):02d}"
            else:
                return f"{minutes}:{int(seconds):02d}"
    except:
        pass
    
    return time_str

def search_dean_content(conn):
    """Search for all Dean-related content across episodes < 232."""
    cursor = conn.cursor()
    
    # Get videos with episode numbers < 232
    cursor.execute("SELECT video_id, title FROM videos ORDER BY title;")
    all_videos = cursor.fetchall()
    
    target_video_ids = []
    episode_map = {}
    for video in all_videos:
        episode_num = extract_episode_number(video['title'])
        if 0 < episode_num < 232:
            target_video_ids.append(video['video_id'])
            episode_map[video['video_id']] = episode_num
    
    print(f"Searching {len(target_video_ids)} episodes for Dean content...\n")
    
    # Search for all Dean-related content
    placeholders = ','.join(['?' for _ in target_video_ids])
    
    query = f"""
    SELECT c.video_id, c.start_time, c.end_time, c.text, v.title, c.sequence_number
    FROM captions c
    JOIN videos v ON c.video_id = v.video_id
    WHERE c.video_id IN ({placeholders})
    AND (c.text LIKE '%dean%' OR c.text LIKE '%Dean%')
    ORDER BY v.title, c.start_time;
    """
    
    cursor.execute(query, target_video_ids)
    dean_results = cursor.fetchall()
    
    print(f"Found {len(dean_results)} segments mentioning 'dean' or 'Dean':")
    print("=" * 80)
    
    current_episode = None
    for row in dean_results:
        episode_num = episode_map.get(row['video_id'], 0)
        
        if current_episode != episode_num:
            current_episode = episode_num
            print(f"\n--- EPISODE {episode_num} ---")
            print(f"Title: {row['title']}")
            print("-" * 60)
        
        start_time = format_timestamp(row['start_time'])
        print(f"{start_time}: {row['text']}")
        
        # Check if this mentions junior dean specifically
        if 'junior' in row['text'].lower() and 'dean' in row['text'].lower():
            print("  *** JUNIOR DEAN MENTION ***")
        
        # Check for authority/character terms in the same segment
        text_lower = row['text'].lower()
        authority_terms = ['authority', 'authoritarian', 'character', 'nature', 'temperament', 'wouldn', 'couldn', 'refuse', 'decline']
        found_terms = [term for term in authority_terms if term in text_lower]
        if found_terms:
            print(f"  >>> Also contains: {', '.join(found_terms)}")
    
    # Now search for context around junior dean mentions
    print(f"\n{'='*80}")
    print("DETAILED CONTEXT FOR JUNIOR DEAN MENTIONS")
    print(f"{'='*80}")
    
    for row in dean_results:
        if 'junior' in row['text'].lower() and 'dean' in row['text'].lower():
            episode_num = episode_map.get(row['video_id'], 0)
            start_time = format_timestamp(row['start_time'])
            
            print(f"\nEPISODE {episode_num} - Junior Dean mention at {start_time}")
            print(f"Target segment: {row['text']}")
            print("-" * 60)
            
            # Get surrounding context
            context_query = """
            SELECT start_time, end_time, text, sequence_number
            FROM captions
            WHERE video_id = ?
            AND sequence_number BETWEEN ? AND ?
            ORDER BY sequence_number;
            """
            
            # Get context (10 segments before and after)
            start_seq = max(0, row['sequence_number'] - 10)
            end_seq = row['sequence_number'] + 10
            
            cursor.execute(context_query, (row['video_id'], start_seq, end_seq))
            context_segments = cursor.fetchall()
            
            for ctx_segment in context_segments:
                ctx_time = format_timestamp(ctx_segment['start_time'])
                marker = " >>> " if ctx_segment['sequence_number'] == row['sequence_number'] else "     "
                print(f"{marker}{ctx_time}: {ctx_segment['text']}")
    
    # Search for authority-related content around Dean mentions
    print(f"\n{'='*80}")
    print("AUTHORITY/CHARACTER CONTENT NEAR DEAN MENTIONS")
    print(f"{'='*80}")
    
    authority_query = f"""
    SELECT c.video_id, c.start_time, c.end_time, c.text, v.title, c.sequence_number
    FROM captions c
    JOIN videos v ON c.video_id = v.video_id
    WHERE c.video_id IN ({placeholders})
    AND (c.text LIKE '%authority%' OR c.text LIKE '%authoritarian%' 
         OR c.text LIKE '%character%' OR c.text LIKE '%nature%' OR c.text LIKE '%temperament%'
         OR c.text LIKE '%wouldn%' OR c.text LIKE '%couldn%' 
         OR c.text LIKE '%refuse%' OR c.text LIKE '%decline%'
         OR c.text LIKE '%harsh%' OR c.text LIKE '%strict%' OR c.text LIKE '%firm%')
    ORDER BY v.title, c.start_time;
    """
    
    cursor.execute(authority_query, target_video_ids)
    authority_results = cursor.fetchall()
    
    print(f"Found {len(authority_results)} segments with authority/character terms...")
    
    # Check if any authority segments are close to dean segments
    for auth_row in authority_results:
        episode_num = episode_map.get(auth_row['video_id'], 0)
        
        # Check if there's a dean mention within 5 segments
        for dean_row in dean_results:
            if (dean_row['video_id'] == auth_row['video_id'] and 
                abs(dean_row['sequence_number'] - auth_row['sequence_number']) <= 5):
                
                print(f"\nEPISODE {episode_num} - Authority/Character content near Dean mention:")
                dean_time = format_timestamp(dean_row['start_time'])
                auth_time = format_timestamp(auth_row['start_time'])
                print(f"  Dean ({dean_time}): {dean_row['text']}")
                print(f"  Authority ({auth_time}): {auth_row['text']}")
                break

def main():
    conn = connect_to_db()
    if not conn:
        print("Could not connect to database")
        return
    
    try:
        search_dean_content(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()