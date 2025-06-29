#!/usr/bin/env python3
"""
Focused search for the specific Lewis content about administrative positions.
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

def search_promising_leads(conn: sqlite3.Connection):
    """Search the most promising results from previous search."""
    cursor = conn.cursor()
    
    # Get videos with episode numbers < 232
    cursor.execute("SELECT video_id, title FROM videos ORDER BY title;")
    all_videos = cursor.fetchall()
    
    target_video_ids = []
    for video in all_videos:
        episode_num = extract_episode_number(video['title'])
        if 0 < episode_num < 232:
            target_video_ids.append(video['video_id'])
    
    placeholders = ','.join(['?' for _ in target_video_ids])
    
    print("=== MOST PROMISING RESULTS ===\n")
    
    # Look for the specific segments that seemed most relevant
    promising_searches = [
        # From Episode 37 - job offer at a college
        ("Episode 37", "offered at.*College.*job.*Lewis"),
        
        # From Episode 19 - someone got job instead of Lewis
        ("Episode 19", "got the job instead of Lewis"),
        
        # From Episode 24 - position given to someone else 
        ("Episode 24", "position.*threw.*speculation"),
        
        # From Episode 15 - refusing to do something and leaving in a position
        ("Episode 15", "refused absolutely"),
        
        # From Episode 1 - offered position
        ("Episode 1", "offered.*position"),
        
        # From Episode 12 - junior Dean opportunity 
        ("Episode 12", "junior Dean opportunity"),
        
        # Look for Lewis being offered specific positions
        ("Any", "Lewis.*offered"),
        ("Any", "offered.*Lewis"),
        
        # Look for Lewis declining/refusing positions
        ("Any", "Lewis.*decline"),
        ("Any", "Lewis.*refused"),
        ("Any", "Lewis.*turn.*down"),
        
        # Look for character/temperament discussions with positions
        ("Any", "temperament.*position"),
        ("Any", "character.*administrative"),
        ("Any", "authoritarian.*Lewis"),
        ("Any", "Lewis.*authoritarian"),
        ("Any", "Lewis.*harsh"),
        ("Any", "Lewis.*authority"),
        
        # Look for specific college position discussions
        ("Any", "master.*college.*Lewis"),
        ("Any", "Lewis.*master.*college"),
        ("Any", "president.*college.*Lewis"),
        ("Any", "dean.*Lewis"),
        ("Any", "Lewis.*dean"),
    ]
    
    for episode_hint, search_pattern in promising_searches:
        print(f"\n--- Searching for: {search_pattern} ({episode_hint}) ---")
        
        # Convert search pattern to SQL LIKE pattern
        like_pattern = search_pattern.replace('.*', '%')
        
        query = f"""
        SELECT DISTINCT c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE c.video_id IN ({placeholders})
        AND c.text LIKE '%{like_pattern}%'
        ORDER BY v.title, c.start_time;
        """
        
        try:
            cursor.execute(query, target_video_ids)
            results = cursor.fetchall()
            
            if results:
                for row in results:
                    episode_num = extract_episode_number(row['title'])
                    start_time = format_timestamp(row['start_time'])
                    print(f"Episode {episode_num} at {start_time}:")
                    print(f"  {row['text']}")
                    print()
            else:
                print("  No matches found.")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Now let's look for extended context around the promising episodes
    print("\n=== EXTENDED CONTEXT AROUND PROMISING EPISODES ===\n")
    
    promising_episodes = [1, 12, 15, 19, 24, 37]  # Episodes that showed promising results
    
    for ep_num in promising_episodes:
        print(f"\n--- Episode {ep_num} - All Administrative/Character Content ---")
        
        # Find video_id for this episode
        episode_video_id = None
        for video in all_videos:
            if extract_episode_number(video['title']) == ep_num:
                episode_video_id = video['video_id']
                break
        
        if not episode_video_id:
            print(f"  Episode {ep_num} not found in database")
            continue
        
        # Get all segments with administrative or character terms
        admin_char_query = """
        SELECT c.start_time, c.end_time, c.text
        FROM captions c
        WHERE c.video_id = ?
        AND (c.text LIKE '%position%' OR c.text LIKE '%job%' OR c.text LIKE '%role%' 
             OR c.text LIKE '%president%' OR c.text LIKE '%dean%' OR c.text LIKE '%master%'
             OR c.text LIKE '%administrator%' OR c.text LIKE '%administrative%'
             OR c.text LIKE '%principal%' OR c.text LIKE '%head%' OR c.text LIKE '%director%'
             OR c.text LIKE '%offered%' OR c.text LIKE '%offer%'
             OR c.text LIKE '%declined%' OR c.text LIKE '%decline%' OR c.text LIKE '%refused%'
             OR c.text LIKE '%refuse%' OR c.text LIKE '%turn down%' OR c.text LIKE '%turned down%'
             OR c.text LIKE '%character%' OR c.text LIKE '%nature%' OR c.text LIKE '%temperament%'
             OR c.text LIKE '%authoritarian%' OR c.text LIKE '%authority%' OR c.text LIKE '%harsh%'
             OR c.text LIKE '%Lewis%')
        ORDER BY c.start_time;
        """
        
        cursor.execute(admin_char_query, (episode_video_id,))
        context_results = cursor.fetchall()
        
        if context_results:
            for row in context_results:
                start_time = format_timestamp(row['start_time'])
                print(f"  {start_time}: {row['text']}")
        else:
            print(f"  No relevant content found in Episode {ep_num}")

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

def main():
    conn = connect_to_db()
    if not conn:
        print("Could not connect to database")
        return
    
    try:
        search_promising_leads(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()