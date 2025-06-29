"""Test script for content analysis and OCR-based thumbnail generation."""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.thumbnail.content_analyzer import ContentAnalyzer
from src.thumbnail.generator import ThumbnailGenerator


def test_content_analysis():
    """Test content analysis with sample C.S. Lewis texts."""
    
    print("Testing Content Analysis")
    print("=" * 50)
    
    analyzer = ContentAnalyzer()
    
    # Test samples with different themes
    test_samples = [
        {
            "content": """
            Today at Oxford I had the most peculiar conversation with young Tolkien. 
            He was going on about his invented languages again, creating words for 
            elves and dragons as if they were as real as the students in our tutorial. 
            I must admit, there's something rather wonderful about his enthusiasm for 
            these imaginary realms. Perhaps there's more truth in fairy stories than 
            we academics typically allow.
            """,
            "year": "1929",
            "description": "Oxford conversation with Tolkien"
        },
        {
            "content": """
            The problem of pain continues to trouble me. How can a good God allow 
            suffering? I've been wrestling with this question since my mother's death, 
            and now seeing the horrors of this war, it becomes even more pressing. 
            Yet I cannot escape the feeling that pain may serve some purpose we 
            cannot yet comprehend.
            """,
            "year": "1918",
            "description": "Theological reflection on suffering"
        },
        {
            "content": """
            Had bacon and eggs for breakfast this morning - quite the luxury these days 
            with the rationing. Mrs. Moore prepared them beautifully, though she did 
            scold me for reading at the table again. I suppose I was rather absorbed 
            in Malory's Morte d'Arthur. There's something about those old tales that 
            speaks to the soul in ways that modern literature simply cannot achieve.
            """,
            "year": "1943",
            "description": "Daily life during wartime"
        }
    ]
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n{i}. Testing: {sample['description']}")
        print("-" * 40)
        
        analysis = analyzer.analyze_content(sample["content"], sample["year"])
        
        print(f"Generated Title: '{analysis['title']}'")
        print(f"Detected Year: {analysis['year']}")
        print(f"Themes: {', '.join(analysis['themes']) if analysis['themes'] else 'None detected'}")
        print(f"Key Quote: {analysis['key_quote'][:80]}...")
        print(f"Analysis Method: {analysis['analysis_method']}")


def test_thumbnail_generation():
    """Test thumbnail generation from content."""
    
    print("\n\nTesting Thumbnail Generation")
    print("=" * 50)
    
    generator = ThumbnailGenerator()
    
    # Test content-based generation
    test_content = """
    This morning I had quite the debate with my colleague about the merits of 
    Tom Jones. He thinks Fielding's novel is nothing but frivolous entertainment, 
    but I argued that there's genuine moral instruction woven throughout the 
    narrative. Literature need not be dour to be worthwhile. Sometimes a good 
    story teaches us more about human nature than the most serious treatise.
    """
    
    print("1. Generating thumbnail from content...")
    
    try:
        output_path = generator.generate_from_content(test_content, year="1941")
        if output_path:
            print(f"✅ Content-based thumbnail generated: {output_path}")
        else:
            print("❌ Failed to generate content-based thumbnail")
    except Exception as e:
        print(f"❌ Error generating content-based thumbnail: {e}")
    
    # Test manual generation with extracted info
    print("\n2. Generating thumbnail manually...")
    
    try:
        output_path = generator.generate_thumbnail(
            title="Lewis Defends Tom Jones",
            year="1941",
            output_filename="test_manual_thumbnail.png"
        )
        if output_path:
            print(f"✅ Manual thumbnail generated: {output_path}")
        else:
            print("❌ Failed to generate manual thumbnail")
    except Exception as e:
        print(f"❌ Error generating manual thumbnail: {e}")


def test_year_extraction():
    """Test year extraction from various content formats."""
    
    print("\n\nTesting Year Extraction")
    print("=" * 50)
    
    analyzer = ContentAnalyzer()
    
    test_cases = [
        "In 1924, I began my teaching career at Oxford.",
        "The year was 1935 when I first met Charles Williams.",
        "During 1943, the war was at its most intense.",
        "This letter was written in the autumn of 1950.",
        "No specific year mentioned in this text.",
        "Born in 1898, I have seen many changes in the world.",
    ]
    
    for text in test_cases:
        year = analyzer.extract_year_from_content(text)
        print(f"Text: '{text[:50]}...'")
        print(f"Extracted Year: {year or 'None detected'}\n")


def demonstrate_cli_usage():
    """Show examples of how to use the CLI interface."""
    
    print("\n\nCLI Usage Examples")
    print("=" * 50)
    
    print("To use the thumbnail CLI interface:")
    print()
    print("# Interactive mode (recommended for beginners)")
    print("python thumbnail_cli.py --interactive")
    print()
    print("# Generate from text content")
    print('python thumbnail_cli.py --text "Lewis discusses bacon and literature" --year 1943')
    print()
    print("# Generate from book page image")
    print("python thumbnail_cli.py --image path/to/book_page.jpg --year 1935")
    print()
    print("# Just analyze content without generating")
    print('python thumbnail_cli.py --text "Some Lewis content..." --analyze-only')
    print()
    print("# Custom output filename")
    print('python thumbnail_cli.py --text "Content..." --year 1930 --output my_thumbnail.png')


def main():
    """Run all tests."""
    test_content_analysis()
    test_thumbnail_generation() 
    test_year_extraction()
    demonstrate_cli_usage()
    
    print("\n" + "=" * 50)
    print("✅ Content analysis testing complete!")
    print("💡 Try the interactive CLI: python thumbnail_cli.py --interactive")


if __name__ == "__main__":
    main()