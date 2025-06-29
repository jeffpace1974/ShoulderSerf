#!/usr/bin/env python3
"""
Search for Lewis content about dreams and nightmares.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase
import re
from collections import defaultdict

def format_time_for_url(time_str):
    """Convert time string to YouTube URL format."""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                total_seconds = int(h) * 3600 + int(m) * 60 + int(float(s))
                return str(total_seconds)
            elif len(parts) == 2:
                m, s = parts
                total_seconds = int(m) * 60 + int(float(s))
                return str(total_seconds)
    except:
        pass
    return "0"

def main():
    print("🌙 Searching for Lewis content about dreams and nightmares...\n")
    
    db = CaptionDatabase()
    
    # Dream-related search terms
    dream_terms = [
        'dream', 'dreams', 'dreaming', 'dreamt', 'dreamed',
        'nightmare', 'nightmares', 
        'sleep', 'sleeping', 'slept', 'sleepy', 'asleep',
        'subconscious', 'unconscious', 'vision', 'visions'
    ]
    
    # More specific dream-related phrases
    dream_phrases = [
        ['dream', 'about'],
        ['had', 'dream'],
        ['strange', 'dream'],
        ['vivid', 'dream'],
        ['recurring', 'dream'],
        ['bad', 'dream'],
        ['terrible', 'dream']
    ]
    
    all_results = []
    seen_keys = set()
    
    print("Searching for individual terms...")
    for term in dream_terms:
        results = db.search_enhanced(term, limit=50)
        for result in results:
            key = f"{result['video_id']}_{result['start_time']}_{result['end_time']}"
            if key not in seen_keys:
                seen_keys.add(key)
                all_results.append(result)
        print(f"  {term}: {len(results)} results")
    
    print(f"\nSearching for dream-related phrases...")
    for phrase_words in dream_phrases:
        # Use the multi-word search capability
        phrase = ' '.join(phrase_words)
        results = db.search_enhanced(phrase, limit=30)
        for result in results:
            key = f"{result['video_id']}_{result['start_time']}_{result['end_time']}"
            if key not in seen_keys:
                seen_keys.add(key)
                all_results.append(result)
        print(f"  '{phrase}': {len(results)} results")
    
    print(f"\nTotal unique results found: {len(all_results)}")
    
    # Filter for results that are most likely about Lewis's own dreams
    high_relevance_results = []
    medium_relevance_results = []
    low_relevance_results = []
    
    personal_dream_indicators = [
        r'\b(i|my|jack|lewis).*dream',
        r'dream.*\b(i|my|jack|lewis)',
        r'\b(i|my|jack|lewis).*nightmare',
        r'nightmare.*\b(i|my|jack|lewis)',
        r'\b(i|jack|lewis).*sleep',
        r'sleep.*\b(i|jack|lewis)',
        r'\bhad.*dream',
        r'dream.*last night',
        r'woke up',
        r'falling asleep'
    ]
    
    for result in all_results:
        text_lower = result['text'].lower()
        title_lower = result['title'].lower()
        
        # Check for personal dream indicators
        personal_match = False
        for pattern in personal_dream_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                personal_match = True
                break
        
        # Categorize by relevance
        if personal_match:
            high_relevance_results.append(result)
        elif any(term in text_lower for term in ['dream', 'nightmare', 'sleep']):
            if any(term in text_lower for term in ['lewis', 'jack', 'my', 'i ']):
                medium_relevance_results.append(result)
            else:
                low_relevance_results.append(result)
        else:
            low_relevance_results.append(result)
    
    # Sort results by upload date (newest first)
    def sort_by_date(results):
        return sorted(results, key=lambda x: x.get('upload_date', ''), reverse=True)
    
    high_relevance_results = sort_by_date(high_relevance_results)
    medium_relevance_results = sort_by_date(medium_relevance_results)
    low_relevance_results = sort_by_date(low_relevance_results)
    
    print("\n" + "="*80)
    print("🔥 HIGH RELEVANCE: Lewis discussing his own dreams/nightmares")
    print("="*80)
    
    for i, result in enumerate(high_relevance_results[:15]):
        time_url = format_time_for_url(result['start_time'])
        print(f"\n{i+1}. {result['title']}")
        print(f"   📺 https://www.youtube.com/watch?v={result['video_id']}&t={time_url}s")
        print(f"   ⏰ {result['start_time']} - {result['end_time']}")
        print(f"   💬 \"{result['text']}\"")
        if result.get('thumbnail_text'):
            print(f"   🖼️  Thumbnail: {result['thumbnail_text']}")
    
    print("\n" + "="*80)
    print("⭐ MEDIUM RELEVANCE: Lewis mentioning dreams/sleep")
    print("="*80)
    
    for i, result in enumerate(medium_relevance_results[:10]):
        time_url = format_time_for_url(result['start_time'])
        print(f"\n{i+1}. {result['title']}")
        print(f"   📺 https://www.youtube.com/watch?v={result['video_id']}&t={time_url}s")
        print(f"   ⏰ {result['start_time']} - {result['end_time']}")
        print(f"   💬 \"{result['text']}\"")
    
    print("\n" + "="*80)
    print("📊 SUMMARY STATISTICS")
    print("="*80)
    print(f"High relevance results: {len(high_relevance_results)}")
    print(f"Medium relevance results: {len(medium_relevance_results)}")
    print(f"Low relevance results: {len(low_relevance_results)}")
    print(f"Total results: {len(all_results)}")
    
    # Group by video for easier analysis
    videos_with_dream_content = defaultdict(list)
    for result in high_relevance_results + medium_relevance_results:
        videos_with_dream_content[result['video_id']].append(result)
    
    print(f"\nVideos containing dream content: {len(videos_with_dream_content)}")
    
    print("\n" + "="*80)
    print("📹 VIDEOS WITH MULTIPLE DREAM REFERENCES")
    print("="*80)
    
    for video_id, results in videos_with_dream_content.items():
        if len(results) > 1:
            first_result = results[0]
            print(f"\n🎬 {first_result['title']}")
            print(f"   📺 https://www.youtube.com/watch?v={video_id}")
            print(f"   📅 {first_result.get('upload_date', 'Unknown date')}")
            print(f"   🔢 {len(results)} dream-related segments")
            
            for j, segment in enumerate(results[:3]):  # Show first 3 segments
                time_url = format_time_for_url(segment['start_time'])
                print(f"     {j+1}. {segment['start_time']}: \"{segment['text'][:100]}...\"")
                print(f"        🔗 https://www.youtube.com/watch?v={video_id}&t={time_url}s")

if __name__ == "__main__":
    main()