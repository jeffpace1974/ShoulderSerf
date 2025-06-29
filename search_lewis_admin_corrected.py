#!/usr/bin/env python3
"""
Search for Lewis discussing administrative positions and concerns about being authoritarian.
Updated to work with the actual database structure.
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

def extract_episode_number(title: str) -> int:
    """Extract episode number from title."""
    # Look for various episode number patterns
    patterns = [
        r'Episode (\d+)',
        r'Ep\.? (\d+)',
        r'#(\d+)',
        r'Part (\d+)',
        r'(\d+)\s*-',  # Number followed by dash
        r'^\s*(\d+)',  # Number at start
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0  # Return 0 if no episode number found

def search_administrative_content(conn: sqlite3.Connection) -> List:
    """
    Search for content about Lewis and administrative positions.
    """
    results = []
    cursor = conn.cursor()
    
    # First, let's check for videos with episode numbers < 232
    cursor.execute("SELECT video_id, title FROM videos ORDER BY title;")
    all_videos = cursor.fetchall()
    
    # Filter videos with episode numbers < 232
    target_video_ids = []
    for video in all_videos:
        episode_num = extract_episode_number(video['title'])
        if 0 < episode_num < 232:  # Only include videos with valid episode numbers
            target_video_ids.append(video['video_id'])
    
    print(f"Found {len(target_video_ids)} videos with episode numbers < 232")
    
    if not target_video_ids:
        print("No videos found with episode numbers < 232")
        return []
    
    # Create placeholders for SQL IN clause
    placeholders = ','.join(['?' for _ in target_video_ids])
    
    # Administrative position keywords
    admin_searches = [
        "president", "vice president", "dean", "principal", "vice principal", 
        "administrator", "administrative", "master", "head", "director",
        "provost", "warden", "chancellor"
    ]
    
    # Authority/character concern keywords
    authority_searches = [
        "authoritarian", "harsh", "discipline", "authority", "firm", "strict",
        "hard", "tough", "demanding", "severe", "rigid", "inflexible",
        "wouldn't be good", "not suited", "not cut out", "couldn't", "unable",
        "too soft", "too kind", "too gentle", "weakness", "character", "nature",
        "personality", "temperament", "decline", "declined", "turn down", "turned down",
        "refuse", "refused", "reject", "rejected"
    ]
    
    # Use FTS5 search for better performance
    print("\n=== SEARCHING FOR ADMINISTRATIVE POSITIONS ===")
    
    for term in admin_searches:
        fts_query = f"""
        SELECT DISTINCT c.id, c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions_fts cf
        JOIN captions c ON cf.rowid = c.id
        JOIN videos v ON c.video_id = v.video_id
        WHERE captions_fts MATCH '{term}'
        AND c.video_id IN ({placeholders})
        ORDER BY v.title, c.start_time;
        """
        
        cursor.execute(fts_query, target_video_ids)
        term_results = cursor.fetchall()
        
        if term_results:
            print(f"\nFound {len(term_results)} results for '{term}':")
            for row in term_results[:3]:  # Show first 3 results
                episode_num = extract_episode_number(row['title'])
                print(f"  Episode {episode_num}: {row['text'][:100]}...")
            
            results.extend(term_results)
    
    print(f"\n=== SEARCHING FOR AUTHORITY/CHARACTER CONCERNS ===")
    
    for term in authority_searches:
        fts_query = f"""
        SELECT DISTINCT c.id, c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions_fts cf
        JOIN captions c ON cf.rowid = c.id
        JOIN videos v ON c.video_id = v.video_id
        WHERE captions_fts MATCH '{term}'
        AND c.video_id IN ({placeholders})
        ORDER BY v.title, c.start_time;
        """
        
        cursor.execute(fts_query, target_video_ids)
        term_results = cursor.fetchall()
        
        if term_results:
            print(f"\nFound {len(term_results)} results for '{term}':")
            for row in term_results[:3]:  # Show first 3 results
                episode_num = extract_episode_number(row['title'])
                print(f"  Episode {episode_num}: {row['text'][:100]}...")
            
            results.extend(term_results)
    
    # Search for combined terms (admin + character concerns)
    print(f"\n=== SEARCHING FOR COMBINED TERMS ===")
    
    combined_searches = [
        "president AND (authoritarian OR harsh OR authority)",
        "dean AND (character OR nature OR temperament)",
        "administrative AND (decline OR refused OR \"not suited\")",
        "position AND (\"wouldn't\" OR \"couldn't\" OR \"too soft\")",
        "master AND (oxford OR cambridge) AND (authority OR discipline)"
    ]
    
    for search_term in combined_searches:
        fts_query = f"""
        SELECT DISTINCT c.id, c.video_id, c.start_time, c.end_time, c.text, v.title
        FROM captions_fts cf
        JOIN captions c ON cf.rowid = c.id
        JOIN videos v ON c.video_id = v.video_id
        WHERE captions_fts MATCH '{search_term}'
        AND c.video_id IN ({placeholders})
        ORDER BY v.title, c.start_time;
        """
        
        try:
            cursor.execute(fts_query, target_video_ids)
            term_results = cursor.fetchall()
            
            if term_results:
                print(f"\nFound {len(term_results)} results for combined search '{search_term}':")
                for row in term_results:
                    episode_num = extract_episode_number(row['title'])
                    print(f"  Episode {episode_num}: {row['text'][:150]}...")
                
                results.extend(term_results)
        except sqlite3.OperationalError as e:
            print(f"Search failed for '{search_term}': {e}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for row in results:
        key = (row['video_id'], row['start_time'], row['text'])
        if key not in seen:
            seen.add(key)
            unique_results.append(row)
    
    return unique_results

def format_timestamp(time_str):
    """Convert timestamp string to readable format."""
    if not time_str:
        return "N/A"
    
    # Parse HH:MM:SS.mmm format
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
        results = search_administrative_content(conn)
        
        if not results:
            print("\nNo results found matching the search criteria.")
            return
        
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE SEARCH RESULTS: {len(results)} unique segments found")
        print(f"{'='*80}\n")
        
        # Group results by episode
        episodes = {}
        for row in results:
            episode_num = extract_episode_number(row['title'])
            if episode_num not in episodes:
                episodes[episode_num] = {
                    'title': row['title'],
                    'segments': []
                }
            episodes[episode_num]['segments'].append(row)
        
        # Sort by episode number
        for episode_num in sorted(episodes.keys()):
            episode_data = episodes[episode_num]
            print(f"\n{'─'*60}")
            print(f"EPISODE {episode_num}: {episode_data['title']}")
            print(f"{'─'*60}")
            
            # Sort segments by start time
            segments = sorted(episode_data['segments'], key=lambda x: x['start_time'])
            
            for segment in segments:
                start_time = format_timestamp(segment['start_time'])
                end_time = format_timestamp(segment['end_time'])
                
                print(f"\nTimestamp: {start_time} - {end_time}")
                print(f"Text: {segment['text']}")
                print(f"Video ID: {segment['video_id']}")
                
                # Check if this looks particularly relevant
                text_lower = segment['text'].lower()
                admin_words = ['president', 'dean', 'administrator', 'administrative', 'master', 'principal']
                character_words = ['authoritarian', 'harsh', 'character', 'authority', 'wouldn', 'couldn', 'not suited', 'too soft']
                
                has_admin = any(word in text_lower for word in admin_words)
                has_character = any(word in text_lower for word in character_words)
                
                if has_admin and has_character:
                    print("*** HIGHLY RELEVANT: Contains both administrative and character terms ***")
                print()
        
        # Also search for specific key phrases that might be less common
        print(f"\n{'='*80}")
        print("ADDITIONAL TARGETED SEARCHES")
        print(f"{'='*80}\n")
        
        cursor = conn.cursor()
        
        # Get target video IDs again
        cursor.execute("SELECT video_id, title FROM videos ORDER BY title;")
        all_videos = cursor.fetchall()
        target_video_ids = []
        for video in all_videos:
            episode_num = extract_episode_number(video['title'])
            if 0 < episode_num < 232:
                target_video_ids.append(video['video_id'])
        
        placeholders = ','.join(['?' for _ in target_video_ids])
        
        # Search for specific phrases
        phrase_searches = [
            ("offered AND position", "Lewis being offered a position"),
            ("declined AND (role OR position OR job)", "Lewis declining roles"),
            ("oxford AND (master OR head OR dean)", "Oxford administrative positions"),
            ("cambridge AND (master OR head OR dean)", "Cambridge administrative positions"),
            ("college AND (president OR vice)", "College leadership positions"),
            ("\"too kind\" OR \"too gentle\"", "Character concerns about being too kind/gentle"),
            ("\"not cut out\" OR \"not suited\"", "Lewis saying he's not suited for roles"),
            ("authoritarian AND (nature OR character OR personality)", "Discussion of authoritarian character")
        ]
        
        for search_term, description in phrase_searches:
            print(f"\n{description.upper()}:")
            print("-" * 50)
            
            fts_query = f"""
            SELECT DISTINCT c.id, c.video_id, c.start_time, c.end_time, c.text, v.title
            FROM captions_fts cf
            JOIN captions c ON cf.rowid = c.id
            JOIN videos v ON c.video_id = v.video_id
            WHERE captions_fts MATCH '{search_term}'
            AND c.video_id IN ({placeholders})
            ORDER BY v.title, c.start_time;
            """
            
            try:
                cursor.execute(fts_query, target_video_ids)
                phrase_results = cursor.fetchall()
                
                if phrase_results:
                    for row in phrase_results:
                        episode_num = extract_episode_number(row['title'])
                        start_time = format_timestamp(row['start_time'])
                        print(f"Episode {episode_num} at {start_time}: {row['text']}")
                else:
                    print("No results found.")
            except sqlite3.OperationalError as e:
                print(f"Search failed: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()