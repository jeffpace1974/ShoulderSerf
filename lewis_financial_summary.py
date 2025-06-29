#!/usr/bin/env python3
"""
Generate a comprehensive summary of Lewis's financial troubles and father correspondence.
"""

import os
import sys
import sqlite3
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase

def generate_financial_summary():
    """Generate a comprehensive summary of Lewis's financial issues."""
    
    db = CaptionDatabase()
    
    print("=== C.S. LEWIS FINANCIAL TROUBLES AND FATHER CORRESPONDENCE ===")
    print("=== COMPREHENSIVE RESEARCH SUMMARY ===\n")
    
    # Key episodes with detailed financial context
    key_findings = [
        {
            "episode": "ep145 (1922 Diary and Letters Part 29)",
            "video_id": "F3b84bHDGf8",
            "date": "2025-02-01",
            "key_quote": "told him that he wasn't having any money troubles but his father found a bank",
            "context": "Lewis was not being truthful about his financial situation to his father"
        },
        {
            "episode": "ep171 (1922 Diary and Letters Part 48)", 
            "video_id": "ogWppT20-ZE",
            "date": "2025-03-02",
            "key_quote": "was going on with his money um and his father confronted him about it",
            "context": "Father confronted Lewis about his money management"
        },
        {
            "episode": "ep208 (1924 Diary and Letters Part 4)",
            "video_id": "6f4JRhRxbw0", 
            "date": "2025-04-28",
            "key_quote": "father who was pressing him about giving a better account of where all the money",
            "context": "Father demanding accountability for money sent to Lewis"
        },
        {
            "episode": "ep213 (1924 Diary and Letters Part 9)",
            "video_id": "IdIJ1FqFKBc",
            "date": "2025-05-08", 
            "key_quote": "his father is wondering where all the money that he's sending him is going",
            "context": "Father questioning where the money he sends goes"
        },
        {
            "episode": "ep218 (1924 Diary and Letters Part 14)",
            "video_id": "aCzbRilRVfY",
            "date": "2025-05-16",
            "key_quote": "has been hiding, you know, what's been going on with his money when his father sometimes asks",
            "context": "Lewis actively hiding his financial activities from his father"
        }
    ]
    
    print("=== KEY FINDINGS ===\n")
    
    for i, finding in enumerate(key_findings, 1):
        print(f"{i}. {finding['episode']}")
        print(f"   Date: {finding['date']}")
        print(f"   Key Quote: \"{finding['key_quote']}\"")
        print(f"   Context: {finding['context']}")
        print(f"   YouTube: https://www.youtube.com/watch?v={finding['video_id']}")
        print()
    
    # Get specific quotes about money troubles and letters
    money_trouble_quotes = [
        "told him that he wasn't having any money troubles but his father found a bank",
        "if you're having so much trouble with money, um, you can come",
        "father who was pressing him about giving a better account of where all the money",
        "his father is wondering where all the money that he's sending him is going",
        "has been hiding, you know, what's been going on with his money"
    ]
    
    letter_quotes = [
        "spent the whole morning composing a long and difficult letter to my father",
        "a letter from my father this morning answering my last in which I had pointed out that my scholarship had now ceased",
        "one that he wrote to his father",
        "in some of the letters as to uh how much money he would need um and what he's using it for"
    ]
    
    print("=== SPECIFIC MONEY TROUBLE QUOTES ===\n")
    for quote in money_trouble_quotes:
        print(f"• \"{quote}\"")
    print()
    
    print("=== LETTER/CORRESPONDENCE QUOTES ===\n") 
    for quote in letter_quotes:
        print(f"• \"{quote}\"")
    print()
    
    # Get detailed context from key episodes
    print("=== DETAILED FINANCIAL CONTEXT ===\n")
    
    print("1. THE HIDDEN LIVING ARRANGEMENT")
    print("   Lewis was living secretly with Mrs. Moore and her daughter Maureen,")
    print("   using money from his father (who was unaware of this arrangement)")
    print("   to support not just his studies but an entire household.")
    print()
    
    print("2. FATHER'S GROWING SUSPICION") 
    print("   Albert Lewis (the father) became increasingly suspicious about")
    print("   where all the money he was sending was going, as it seemed")
    print("   excessive for a single student's expenses.")
    print()
    
    print("3. LEWIS'S DECEPTION")
    print("   Lewis was actively hiding his true living situation and")
    print("   financial needs from his father, sometimes lying about")
    print("   what he needed money for.")
    print()
    
    print("4. CONFRONTATIONS AND PRESSURE")
    print("   The father repeatedly confronted Lewis and pressed him")
    print("   for better accounting of the money, creating ongoing tension.")
    print()
    
    print("5. DIFFICULT CORRESPONDENCE")
    print("   Lewis had to write 'long and difficult' letters to his father")
    print("   explaining his financial needs while concealing the true reasons.")
    print()
    
    # Search for additional specific details
    additional_searches = [
        "thirty pounds extra expenses",
        "scholarship had now ceased", 
        "supplement to carry on",
        "cannot account for at all",
        "bank account",
        "allowance"
    ]
    
    print("=== ADDITIONAL FINANCIAL DETAILS ===\n")
    
    for term in additional_searches:
        results = db.search_enhanced(term, limit=3)
        if results:
            print(f"Search: \"{term}\"")
            for result in results:
                time_seconds = convert_time_to_seconds(result['start_time'])
                print(f"  • {result['title']}")
                print(f"    Time: {result['start_time']} | Link: https://www.youtube.com/watch?v={result['video_id']}&t={time_seconds}s")
                print(f"    Quote: \"{result['text']}\"")
            print()
    
    print("=== RESEARCH CONCLUSION ===\n")
    print("The evidence shows a clear pattern of financial deception and tension")
    print("between Lewis and his father during his Oxford years (1921-1924).")
    print("Lewis was using his father's money to support a secret household")
    print("arrangement while lying about his actual financial needs and situation.")
    print("This created ongoing conflict and required Lewis to write difficult")
    print("letters trying to justify his expenses without revealing the truth.")

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
    generate_financial_summary()