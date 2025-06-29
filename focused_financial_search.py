#!/usr/bin/env python3
"""
Focused search for Lewis financial content - optimized for speed.
"""

import os
import sys
import sqlite3
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase

def focused_financial_search():
    """Search for Lewis financial content using high-priority terms only."""
    
    db = CaptionDatabase()
    
    # High-priority financial search terms
    priority_terms = [
        "money trouble", "money troubles", "financial trouble", "financial troubles",
        "father about money", "wrote to father", "letter to father", 
        "debt", "expenses", "financial", "money", "father", "poor", "bills"
    ]
    
    print("=== LEWIS FINANCIAL CONTENT SEARCH ===\n")
    
    all_results = []
    
    for term in priority_terms:
        print(f"Searching for: {term}")
        results = db.search_enhanced(term, limit=20)
        
        if results:
            print(f"  Found {len(results)} results")
            for result in results:
                result['search_term'] = term
                all_results.append(result)
        else:
            print(f"  No results found")
    
    # Remove duplicates based on video_id + start_time
    seen = set()
    unique_results = []
    for result in all_results:
        key = f"{result['video_id']}_{result['start_time']}"
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    print(f"\nTotal unique results: {len(unique_results)}")
    
    # Sort by relevance
    def relevance_score(result):
        text = result['text'].lower()
        score = 0
        
        # High scores for specific combinations
        if 'father' in text and 'money' in text:
            score += 10
        if 'letter' in text and ('money' in text or 'financial' in text):
            score += 8
        if 'trouble' in text and 'money' in text:
            score += 6
        if 'debt' in text:
            score += 5
        if 'expense' in text or 'bill' in text:
            score += 3
            
        return score
    
    unique_results.sort(key=relevance_score, reverse=True)
    
    # Display top results
    print(f"\n=== TOP RESULTS ===\n")
    
    for i, result in enumerate(unique_results[:15], 1):
        print(f"RESULT {i} (Score: {relevance_score(result)})")
        print(f"Video: {result['title']}")
        print(f"Date: {result['upload_date']}")
        print(f"Time: {result['start_time']} - {result['end_time']}")
        print(f"Search term: {result['search_term']}")
        
        # Convert time to seconds for URL
        time_seconds = convert_time_to_seconds(result['start_time'])
        print(f"YouTube: https://www.youtube.com/watch?v={result['video_id']}&t={time_seconds}s")
        
        print(f"\nCaption: {result['text']}")
        print("=" * 70)
        print()

def convert_time_to_seconds(time_str):
    """Convert timestamp to seconds for YouTube URL."""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(float(s))
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + int(float(s))
    except:
        pass
    return 0

if __name__ == '__main__':
    focused_financial_search()