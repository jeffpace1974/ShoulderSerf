#!/usr/bin/env python3
"""
Detailed search for Lewis financial content with specific focus on key episodes.
"""

import os
import sys
import sqlite3
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase

def get_episode_financial_context():
    """Get detailed financial context from key episodes."""
    
    db = CaptionDatabase()
    
    # Key video IDs from the search results that show high financial relevance
    key_episodes = [
        "F3b84bHDGf8",  # ep145 - money troubles
        "ogWppT20-ZE",  # ep171 - father confronted him about money
        "6f4JRhRxbw0",  # ep208 - father pressing about money account
        "Kmlo5m68nms",  # ep207 - what he's doing with father's money
        "6WwvSCSRLAI",  # ep201 - father's money stories
        "dV-2MdSu0K0",  # ep112 - prize money discussion
        "xBWulCq82kk",  # ep115 - discussion about money usage
        "1KHeBY9qymw",  # ep206 - lying about needing money
        "aCzbRilRVfY",  # ep218 - hiding money matters
        "IdIJ1FqFKBc",  # ep213 - father wondering where money goes
        "7UbjNNetYfI",  # ep209 - trouble with money
    ]
    
    print("=== DETAILED LEWIS FINANCIAL CONTEXT ===\n")
    
    for video_id in key_episodes:
        video_info = db.get_video_info(video_id)
        if video_info:
            print(f"=== {video_info['title']} ===")
            print(f"Date: {video_info['upload_date']}")
            print(f"YouTube: https://www.youtube.com/watch?v={video_id}")
            print()
            
            # Get all captions from this video that mention financial terms
            captions = db.get_video_captions(video_id)
            
            financial_keywords = [
                'money', 'financial', 'father', 'debt', 'expense', 'cost', 'bill', 
                'poor', 'trouble', 'need', 'send', 'sending', 'account', 'hiding',
                'lying', 'confronted', 'pressing', 'prize', 'allowance'
            ]
            
            relevant_captions = []
            for caption in captions:
                text_lower = caption['text'].lower()
                if any(keyword in text_lower for keyword in financial_keywords):
                    relevant_captions.append(caption)
            
            # Group consecutive captions for better context
            grouped_captions = []
            current_group = []
            
            for i, caption in enumerate(relevant_captions):
                if current_group:
                    # Check if this caption is consecutive to the last one in the group
                    last_caption = current_group[-1]
                    current_seq = caption.get('sequence_number', 0)
                    last_seq = last_caption.get('sequence_number', 0)
                    
                    if current_seq - last_seq <= 3:  # Allow small gaps
                        current_group.append(caption)
                    else:
                        grouped_captions.append(current_group)
                        current_group = [caption]
                else:
                    current_group = [caption]
            
            if current_group:
                grouped_captions.append(current_group)
            
            # Display grouped captions
            for group_idx, group in enumerate(grouped_captions[:5], 1):  # Show top 5 groups
                print(f"Context {group_idx}:")
                start_time = group[0]['start_time']
                end_time = group[-1]['end_time']
                time_seconds = convert_time_to_seconds(start_time)
                print(f"Time: {start_time} - {end_time}")
                print(f"Link: https://www.youtube.com/watch?v={video_id}&t={time_seconds}s")
                
                combined_text = ' '.join([cap['text'] for cap in group])
                print(f"Text: {combined_text}")
                print()
            
            print("-" * 80)
            print()

def search_specific_themes():
    """Search for specific financial themes."""
    
    db = CaptionDatabase()
    
    themes = {
        "Father's Money Concerns": [
            "father confronted", "father pressing", "father wondering", 
            "father found", "father asks", "father questions"
        ],
        "Lewis's Deception/Hiding": [
            "hiding", "lying", "concealing", "deceiving", "not telling",
            "false account", "misleading"
        ],
        "Money Problems": [
            "money trouble", "financial trouble", "need money", "short of money",
            "no money", "running out", "expensive", "can't afford"
        ],
        "Letters & Correspondence": [
            "wrote to father", "letter to father", "letters about money",
            "correspondence", "telegram", "writing home"
        ],
        "University Expenses": [
            "university costs", "college expenses", "tuition", "Oxford costs",
            "living expenses", "room and board", "textbooks"
        ]
    }
    
    print("=== THEMATIC FINANCIAL CONTENT ===\n")
    
    for theme, terms in themes.items():
        print(f"=== {theme.upper()} ===")
        
        theme_results = []
        for term in terms:
            results = db.search_enhanced(term, limit=10)
            theme_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in theme_results:
            key = f"{result['video_id']}_{result['start_time']}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by date
        unique_results.sort(key=lambda x: x['upload_date'] or '', reverse=True)
        
        for result in unique_results[:5]:  # Top 5 per theme
            time_seconds = convert_time_to_seconds(result['start_time'])
            print(f"• {result['title']}")
            print(f"  Time: {result['start_time']} | Link: https://www.youtube.com/watch?v={result['video_id']}&t={time_seconds}s")
            print(f"  Text: {result['text']}")
            print()
        
        print("-" * 60)
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
    get_episode_financial_context()
    print("\n" + "="*80 + "\n")
    search_specific_themes()