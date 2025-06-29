#!/usr/bin/env python3
"""
Test the new entity extraction functionality.
"""

from intelligent_claude_search import IntelligentClaudeSearch

def test_extraction():
    search = IntelligentClaudeSearch()
    
    # Test with query about Luke Thompson movies
    query = "luke thompson movie favorite film"
    
    print(f"Testing query: {query}")
    print("=" * 50)
    
    # Understand the query
    understanding = search.understand_query(query)
    print(f"Query understanding: {understanding}")
    
    # Search with intelligence
    results = search.search_with_intelligence(understanding)
    print(f"Found {len(results)} results")
    
    # Test entity extraction specifically on results
    extractions = search._extract_key_entities_from_results(results, query)
    print(f"\nExtracted entities: {len(extractions)}")
    
    for i, extraction in enumerate(extractions):
        print(f"{i+1}. Type: {extraction['type']}")
        print(f"   Value: {extraction['value']}")
        print(f"   Context: {extraction['context']}")
        print(f"   Episode: {extraction.get('episode', 'N/A')}")
        print(f"   Source: {extraction['source_text'][:100]}...")
        print()

if __name__ == "__main__":
    test_extraction()