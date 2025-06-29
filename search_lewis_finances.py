#!/usr/bin/env python3
"""
Search for Lewis financial content in the captions database.
Focus on finding mentions of money troubles, correspondence with father about finances.
"""

import os
import sys
import sqlite3
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase

def search_financial_content():
    """Search for Lewis financial content using multiple search terms."""
    
    db = CaptionDatabase()
    
    # Financial search terms - comprehensive list
    financial_terms = [
        # Direct financial terms
        "money", "financial", "finances", "debt", "debts", "expenses", "expense", 
        "income", "salary", "wages", "pay", "payment", "payments", "bills", "bill",
        "cost", "costs", "costly", "expensive", "cheap", "afford", "poverty", "poor",
        "rich", "wealth", "wealthy", "cash", "funds", "budget", "budgeting",
        
        # Father-related terms
        "father", "dad", "daddy", "albert", "papa", "parent", "parents",
        "family money", "family finances", "family financial",
        
        # Letter/correspondence terms
        "letter", "letters", "wrote", "writing", "correspondence", "mail",
        "telegram", "postcards", "wrote to his father", "wrote father",
        
        # Trouble/difficulty terms
        "trouble", "troubles", "difficulty", "difficulties", "struggle", "struggles",
        "hard times", "tight", "stretched", "pinched", "crisis", "emergency"
    ]
    
    # Compound search phrases for more specific results
    compound_phrases = [
        "money trouble", "money troubles", "financial trouble", "financial troubles",
        "financial difficulty", "financial difficulties", "money problems",
        "wrote to father", "letter to father", "letters to father",
        "father about money", "father money", "financial crisis",
        "short of money", "need money", "lack of money", "no money",
        "tight financially", "financially tight", "hard up",
        "father financial", "father finances"
    ]
    
    print("=== SEARCHING FOR LEWIS FINANCIAL CONTENT ===\n")
    
    all_results = []
    seen_results = set()
    
    # First search for compound phrases (more specific)
    print("Searching for specific financial phrases...")
    for phrase in compound_phrases:
        results = db.search_enhanced(phrase, limit=100)
        if results:
            print(f"Found {len(results)} results for '{phrase}'")
            for result in results:
                result_key = f"{result['video_id']}_{result['start_time']}_{result['text'][:50]}"
                if result_key not in seen_results:
                    seen_results.add(result_key)
                    result['search_term'] = phrase
                    all_results.append(result)
    
    print(f"\nFound {len(all_results)} unique results from phrase searches\n")
    
    # Then search individual terms
    print("Searching for individual financial terms...")
    term_results = 0
    for term in financial_terms:
        results = db.search_enhanced(term, limit=50)
        if results:
            for result in results:
                result_key = f"{result['video_id']}_{result['start_time']}_{result['text'][:50]}"
                if result_key not in seen_results:
                    seen_results.add(result_key)
                    result['search_term'] = term
                    all_results.append(result)
                    term_results += 1
    
    print(f"Added {term_results} additional results from individual terms\n")
    
    # Sort by relevance (prioritize compound phrases) and date
    def get_relevance_score(result):
        text_lower = result['text'].lower()
        score = 0
        
        # Higher score for compound phrases
        if result['search_term'] in compound_phrases:
            score += 10
        
        # Higher score for father + money combinations
        if 'father' in text_lower and any(term in text_lower for term in ['money', 'financial', 'debt', 'expense']):
            score += 8
            
        # Higher score for letter + financial combinations
        if any(term in text_lower for term in ['letter', 'wrote', 'writing']) and any(term in text_lower for term in ['money', 'financial', 'trouble']):
            score += 6
            
        # Score for multiple financial terms in same caption
        financial_term_count = sum(1 for term in financial_terms if term in text_lower)
        score += financial_term_count
        
        return score
    
    # Sort by relevance score (highest first), then by date
    all_results.sort(key=lambda x: (get_relevance_score(x), x['upload_date'] or ''), reverse=True)
    
    print(f"=== TOTAL RESULTS: {len(all_results)} ===\n")
    
    # Display top results with context
    top_results = all_results[:30]  # Show top 30 most relevant results
    
    for i, result in enumerate(top_results, 1):
        print(f"=== RESULT {i} ===")
        print(f"Video: {result['title']}")
        print(f"Uploader: {result['uploader']}")
        print(f"Date: {result['upload_date']}")
        print(f"Time: {result['start_time']} - {result['end_time']}")
        print(f"Search Term: {result['search_term']}")
        print(f"Relevance Score: {get_relevance_score(result)}")
        print(f"YouTube URL: https://www.youtube.com/watch?v={result['video_id']}&t={convert_time_to_seconds(result['start_time'])}s")
        print(f"\nText: {result['text']}")
        print("-" * 80)
        print()
    
    # Summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total unique results: {len(all_results)}")
    print(f"Top search terms by result count:")
    
    term_counts = {}
    for result in all_results:
        term = result['search_term']
        term_counts[term] = term_counts.get(term, 0) + 1
    
    sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
    for term, count in sorted_terms[:10]:
        print(f"  {term}: {count} results")
    
    # Videos with most financial content
    print(f"\nVideos with most financial mentions:")
    video_counts = {}
    for result in all_results:
        video_key = f"{result['video_id']} - {result['title']}"
        video_counts[video_key] = video_counts.get(video_key, 0) + 1
    
    sorted_videos = sorted(video_counts.items(), key=lambda x: x[1], reverse=True)
    for video, count in sorted_videos[:10]:
        print(f"  {count} mentions: {video}")

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
    search_financial_content()