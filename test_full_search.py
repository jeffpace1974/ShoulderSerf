#!/usr/bin/env python3
"""
Test the full integrated search experience.
"""

from intelligent_claude_search import IntelligentClaudeSearch

def test_full_search():
    search = IntelligentClaudeSearch()
    
    # Test with query about Luke Thompson movies
    query = "luke thompson movie favorite film"
    
    print(f"Testing full search for: {query}")
    print("=" * 60)
    
    # Understand the query
    understanding = search.understand_query(query)
    
    # Search with intelligence
    results = search.search_with_intelligence(understanding)
    
    # Generate the full Claude analysis (what the UI would show)
    analysis = search.generate_claude_analysis(query, results, understanding)
    
    print(analysis)

if __name__ == "__main__":
    test_full_search()