#!/usr/bin/env python3
"""
Detailed search of Episode 12 content around the junior Dean opportunity.
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

def get_context_around_timestamp(conn, video_id, target_time, context_minutes=2):
    """Get context around a specific timestamp."""
    cursor = conn.cursor()
    
    # Convert target time to seconds for comparison
    try:
        parts = target_time.split(':')
        if len(parts) == 3:
            target_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        else:
            return []
    except:
        return []
    
    # Get segments within context_minutes before and after
    start_seconds = max(0, target_seconds - (context_minutes * 60))
    end_seconds = target_seconds + (context_minutes * 60)
    
    query = """
    SELECT start_time, end_time, text, sequence_number
    FROM captions
    WHERE video_id = ?
    ORDER BY sequence_number;
    """
    
    cursor.execute(query, (video_id,))
    all_segments = cursor.fetchall()
    
    context_segments = []
    for segment in all_segments:
        try:
            parts = segment['start_time'].split(':')
            if len(parts) == 3:
                seg_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                if start_seconds <= seg_seconds <= end_seconds:
                    context_segments.append(segment)
        except:
            continue
    
    return context_segments

def search_episode_12_detailed(conn):
    """Detailed search of Episode 12."""
    cursor = conn.cursor()
    
    # Find Episode 12
    cursor.execute("SELECT video_id, title FROM videos;")
    all_videos = cursor.fetchall()
    
    episode_12_video = None
    for video in all_videos:
        if extract_episode_number(video['title']) == 12:
            episode_12_video = video
            break
    
    if not episode_12_video:
        print("Episode 12 not found")
        return
    
    print(f"Episode 12: {episode_12_video['title']}")
    print(f"Video ID: {episode_12_video['video_id']}")
    print("=" * 80)
    
    # Search for all segments containing key terms
    key_terms = [
        'dean', 'Dean', 'junior', 'Junior', 'position', 'job', 'role',
        'authority', 'administrative', 'offer', 'offered', 'decline', 'declined',
        'refuse', 'refused', 'character', 'nature', 'temperament',
        'lewis', 'Lewis', 'would', 'wouldn', 'couldn', 'should'
    ]
    
    # Get all relevant segments
    query = """
    SELECT start_time, end_time, text, sequence_number
    FROM captions
    WHERE video_id = ?
    AND (text LIKE '%dean%' OR text LIKE '%Dean%' 
         OR text LIKE '%junior%' OR text LIKE '%Junior%'
         OR text LIKE '%position%' OR text LIKE '%job%' OR text LIKE '%role%'
         OR text LIKE '%authority%' OR text LIKE '%administrative%'
         OR text LIKE '%offer%' OR text LIKE '%decline%' OR text LIKE '%refuse%'
         OR text LIKE '%character%' OR text LIKE '%nature%' OR text LIKE '%temperament%'
         OR text LIKE '%wouldn%' OR text LIKE '%couldn%' OR text LIKE '%should%')
    ORDER BY sequence_number;
    """
    
    cursor.execute(query, (episode_12_video['video_id'],))
    relevant_segments = cursor.fetchall()
    
    print(f"\nFound {len(relevant_segments)} relevant segments in Episode 12:")
    print("-" * 60)
    
    # Find the junior Dean mention specifically
    junior_dean_segments = []
    for segment in relevant_segments:
        if 'junior' in segment['text'].lower() and 'dean' in segment['text'].lower():
            junior_dean_segments.append(segment)
    
    if junior_dean_segments:
        print("\n*** JUNIOR DEAN MENTIONS ***")
        for segment in junior_dean_segments:
            start_time = format_timestamp(segment['start_time'])
            print(f"{start_time}: {segment['text']}")
            
            # Get extended context around this mention
            print(f"\n--- Extended context around {start_time} ---")
            context = get_context_around_timestamp(conn, episode_12_video['video_id'], segment['start_time'], 3)
            for ctx_segment in context:
                ctx_time = format_timestamp(ctx_segment['start_time'])
                marker = " >>> " if ctx_segment['start_time'] == segment['start_time'] else "     "
                print(f"{marker}{ctx_time}: {ctx_segment['text']}")
    
    # Look for authority-related discussions
    print(f"\n*** AUTHORITY/CHARACTER DISCUSSIONS ***")
    authority_terms = ['authority', 'character', 'nature', 'temperament', 'wouldn', 'couldn', 'should']
    
    for segment in relevant_segments:
        text_lower = segment['text'].lower()
        if any(term in text_lower for term in authority_terms):
            start_time = format_timestamp(segment['start_time'])
            print(f"{start_time}: {segment['text']}")
    
    # Look for Lewis-specific mentions
    print(f"\n*** LEWIS-SPECIFIC CONTENT ***")
    lewis_segments = []
    for segment in relevant_segments:
        if 'lewis' in segment['text'].lower():
            lewis_segments.append(segment)
    
    for segment in lewis_segments:
        start_time = format_timestamp(segment['start_time'])
        print(f"{start_time}: {segment['text']}")
    
    # Show timeline of all relevant segments
    print(f"\n*** COMPLETE TIMELINE OF RELEVANT SEGMENTS ***")
    print("-" * 60)
    
    for segment in relevant_segments:
        start_time = format_timestamp(segment['start_time'])
        # Highlight particularly interesting segments
        markers = []
        text_lower = segment['text'].lower()
        
        if 'dean' in text_lower:
            markers.append("DEAN")
        if 'position' in text_lower or 'job' in text_lower or 'role' in text_lower:
            markers.append("POSITION")
        if 'authority' in text_lower:
            markers.append("AUTHORITY")
        if 'lewis' in text_lower:
            markers.append("LEWIS")
        if 'wouldn' in text_lower or 'couldn' in text_lower:
            markers.append("HESITATION")
        if 'character' in text_lower or 'nature' in text_lower:
            markers.append("CHARACTER")
        
        marker_str = f" [{', '.join(markers)}]" if markers else ""
        print(f"{start_time}: {segment['text']}{marker_str}")

def main():
    conn = connect_to_db()
    if not conn:
        print("Could not connect to database")
        return
    
    try:
        search_episode_12_detailed(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()