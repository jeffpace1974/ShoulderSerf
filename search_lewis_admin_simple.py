#!/usr/bin/env python3
"""
Search for Lewis discussing administrative positions and concerns about being authoritarian.
Simplified version using regular LIKE queries for more reliable results.
"""

import sqlite3
import re
from typing import List

def connect_to_db(db_path: str = "captions.db"):
    """Connect to the captions database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def extract_episode_number(title: str) -> int:
    """Extract episode number from title."""
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

def search_specific_content(conn: sqlite3.Connection) -> List:
    """Search for specific administrative position content."""
    results = []
    cursor = conn.cursor()
    
    # Get videos with episode numbers < 232
    cursor.execute("SELECT video_id, title FROM videos ORDER BY title;")
    all_videos = cursor.fetchall()
    
    target_video_ids = []
    for video in all_videos:
        episode_num = extract_episode_number(video['title'])
        if 0 < episode_num < 232:
            target_video_ids.append(video['video_id'])
    
    print(f"Searching in {len(target_video_ids)} videos with episode numbers < 232\n")
    
    # Search for administrative positions + character concerns in the same segment
    print("=== SEARCHING FOR SEGMENTS WITH BOTH ADMINISTRATIVE AND CHARACTER TERMS ===\n")
    
    admin_terms = ['president', 'dean', 'administrator', 'administrative', 'master', 'principal', 'head', 'position']
    character_terms = ['authoritarian', 'harsh', 'authority', 'character', 'nature', 'wouldn', 'couldn', 'suited', 'soft', 'kind', 'gentle', 'decline', 'refuse', 'turn down']
    
    placeholders = ','.join(['?' for _ in target_video_ids])
    
    for admin_term in admin_terms:
        for char_term in character_terms:
            query = f"""
            SELECT DISTINCT c.video_id, c.start_time, c.end_time, c.text, v.title
            FROM captions c
            JOIN videos v ON c.video_id = v.video_id
            WHERE c.video_id IN ({placeholders})
            AND (c.text LIKE '%{admin_term}%' OR c.text LIKE '%{admin_term.title()}%')
            AND (c.text LIKE '%{char_term}%' OR c.text LIKE '%{char_term.title()}%')
            ORDER BY v.title, c.start_time;
            """
            
            cursor.execute(query, target_video_ids)
            combo_results = cursor.fetchall()
            
            if combo_results:
                print(f"Found {len(combo_results)} segments containing both '{admin_term}' and '{char_term}':")
                for row in combo_results:
                    episode_num = extract_episode_number(row['title'])
                    print(f"  Episode {episode_num}: {row['text']}")
                print()
                results.extend(combo_results)
    
    # Search for specific phrases about positions and character
    print("=== SEARCHING FOR SPECIFIC PHRASES ===\n")
    
    specific_phrases = [
        ("offered", "position"),
        ("offered", "job"), 
        ("offered", "role"),
        ("declined", "position"),
        ("declined", "role"),
        ("turn down", "position"),
        ("refuse", "position"),
        ("not suited", "position"),
        ("not cut out", "position"),
        ("wouldn't be good", "position"),
        ("couldn't", "position"),
        ("too soft", "position"),
        ("too kind", "position"),
        ("character", "president"),
        ("character", "dean"),
        ("nature", "administrative"),
        ("temperament", "authority"),
        ("authoritarian", "president"),
        ("authoritarian", "dean"),
        ("authoritarian", "master"),
        ("harsh", "authority"),
        ("discipline", "position")
    ]
    
    for phrase1, phrase2 in specific_phrases:
        query = f"""
        SELECT DISTINCT c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE c.video_id IN ({placeholders})
        AND c.text LIKE '%{phrase1}%'
        AND c.text LIKE '%{phrase2}%'
        ORDER BY v.title, c.start_time;
        """
        
        cursor.execute(query, target_video_ids)
        phrase_results = cursor.fetchall()
        
        if phrase_results:
            print(f"Found {len(phrase_results)} segments containing '{phrase1}' and '{phrase2}':")
            for row in phrase_results:
                episode_num = extract_episode_number(row['title'])
                print(f"  Episode {episode_num}: {row['text'][:200]}...")
            print()
            results.extend(phrase_results)
    
    # Search for broader context around administrative positions
    print("=== SEARCHING FOR BROADER ADMINISTRATIVE CONTEXT ===\n")
    
    broader_searches = [
        ("oxford", "master"),
        ("cambridge", "master"), 
        ("oxford", "president"),
        ("cambridge", "president"),
        ("college", "president"),
        ("college", "dean"),
        ("university", "position"),
        ("academic", "position"),
        ("administrative", "role"),
        ("lewis", "offered"),
        ("lewis", "declined"),
        ("lewis", "refused")
    ]
    
    for term1, term2 in broader_searches:
        query = f"""
        SELECT DISTINCT c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE c.video_id IN ({placeholders})
        AND (c.text LIKE '%{term1}%' OR c.text LIKE '%{term1.title()}%')
        AND (c.text LIKE '%{term2}%' OR c.text LIKE '%{term2.title()}%')
        ORDER BY v.title, c.start_time;
        """
        
        cursor.execute(query, target_video_ids)
        context_results = cursor.fetchall()
        
        if context_results:
            print(f"Found {len(context_results)} segments with '{term1}' and '{term2}':")
            for row in context_results[:5]:  # Show first 5 results
                episode_num = extract_episode_number(row['title'])
                print(f"  Episode {episode_num}: {row['text'][:150]}...")
            if len(context_results) > 5:
                print(f"  ... and {len(context_results) - 5} more results")
            print()
            results.extend(context_results)
    
    return results

def format_timestamp(time_str):
    """Convert timestamp string to readable format."""
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
        results = search_specific_content(conn)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for row in results:
            key = (row['video_id'], row['start_time'], row['text'])
            if key not in seen:
                seen.add(key)
                unique_results.append(row)
        
        if not unique_results:
            print("No results found matching the search criteria.")
            return
        
        print(f"\n{'='*80}")
        print(f"FINAL RESULTS: {len(unique_results)} unique segments found")
        print(f"{'='*80}\n")
        
        # Group by episode
        episodes = {}
        for row in unique_results:
            episode_num = extract_episode_number(row['title'])
            if episode_num not in episodes:
                episodes[episode_num] = {
                    'title': row['title'],
                    'segments': []
                }
            episodes[episode_num]['segments'].append(row)
        
        # Display results by episode
        for episode_num in sorted(episodes.keys()):
            episode_data = episodes[episode_num]
            print(f"\n{'─'*60}")
            print(f"EPISODE {episode_num}: {episode_data['title']}")
            print(f"{'─'*60}")
            
            segments = sorted(episode_data['segments'], key=lambda x: x['start_time'])
            
            for segment in segments:
                start_time = format_timestamp(segment['start_time'])
                end_time = format_timestamp(segment['end_time'])
                
                print(f"\nTimestamp: {start_time} - {end_time}")
                print(f"Text: {segment['text']}")
                
                # Highlight if this looks particularly relevant
                text_lower = segment['text'].lower()
                admin_in_text = any(word in text_lower for word in ['president', 'dean', 'administrator', 'administrative', 'master', 'principal', 'position'])
                character_in_text = any(word in text_lower for word in ['authoritarian', 'harsh', 'character', 'authority', 'nature', 'wouldn', 'couldn', 'suited', 'soft', 'kind', 'decline', 'refuse'])
                
                if admin_in_text and character_in_text:
                    print("*** HIGHLY RELEVANT: Contains both administrative and character discussion ***")
                
                print(f"Video ID: {segment['video_id']}")
                print()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()