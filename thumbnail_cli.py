#!/usr/bin/env python3
"""
Command-line interface for generating C.S. Lewis episode thumbnails.

Usage:
    # Generate from text content
    python thumbnail_cli.py --text "Lewis discusses his love of bacon and eggs" --year 1924
    
    # Generate from book page image
    python thumbnail_cli.py --image path/to/book_page.jpg --year 1935
    
    # Interactive mode
    python thumbnail_cli.py --interactive
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.thumbnail.generator import ThumbnailGenerator
from src.thumbnail.content_analyzer import ContentAnalyzer


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def generate_from_text(text: str, year: str = None, output: str = None) -> str:
    """Generate thumbnail from text content."""
    generator = ThumbnailGenerator()
    
    print("Analyzing content...")
    output_path = generator.generate_from_content(text, year=year)
    
    if output and output_path:
        # Move to custom output path
        import shutil
        shutil.move(output_path, output)
        output_path = output
    
    return output_path


def generate_from_image(image_path: str, year: str = None, output: str = None) -> str:
    """Generate thumbnail from book page image."""
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return None
    
    generator = ThumbnailGenerator()
    
    print("Extracting text from image...")
    output_path = generator.generate_from_image(image_path, year=year)
    
    if output and output_path:
        # Move to custom output path
        import shutil
        shutil.move(output_path, output)
        output_path = output
    
    return output_path


def interactive_mode():
    """Run in interactive mode for easy thumbnail generation."""
    print("🎨 C.S. Lewis Thumbnail Generator")
    print("=" * 50)
    
    generator = ThumbnailGenerator()
    analyzer = ContentAnalyzer()
    
    while True:
        print("\nOptions:")
        print("1. Generate from text content")
        print("2. Generate from book page image")
        print("3. Generate with custom title and year")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            print("\n📝 Generate from text content")
            text = input("Paste the C.S. Lewis text content:\n").strip()
            
            if not text:
                print("No text provided.")
                continue
            
            year = input("Year (leave blank to auto-detect): ").strip() or None
            
            try:
                output_path = generator.generate_from_content(text, year=year)
                if output_path:
                    print(f"✅ Thumbnail generated: {output_path}")
                else:
                    print("❌ Failed to generate thumbnail")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "2":
            print("\n📷 Generate from book page image")
            image_path = input("Enter path to book page image: ").strip()
            
            if not os.path.exists(image_path):
                print(f"Image file '{image_path}' not found.")
                continue
            
            year = input("Year (leave blank to auto-detect): ").strip() or None
            
            try:
                output_path = generator.generate_from_image(image_path, year=year)
                if output_path:
                    print(f"✅ Thumbnail generated: {output_path}")
                else:
                    print("❌ Failed to generate thumbnail")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "3":
            print("\n✏️  Generate with custom title and year")
            title = input("Enter thumbnail title: ").strip()
            year = input("Enter year: ").strip()
            
            if not title or not year:
                print("Both title and year are required.")
                continue
            
            try:
                output_path = generator.generate_thumbnail(title, year)
                if output_path:
                    print(f"✅ Thumbnail generated: {output_path}")
                else:
                    print("❌ Failed to generate thumbnail")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-4.")


def analyze_content_only(text: str = None, image_path: str = None):
    """Just analyze content without generating thumbnail."""
    analyzer = ContentAnalyzer()
    
    if image_path:
        print("Extracting text from image...")
        text = analyzer.extract_text_from_image(image_path)
        print(f"Extracted text ({len(text)} chars):")
        print("-" * 40)
        print(text[:500] + ("..." if len(text) > 500 else ""))
        print("-" * 40)
    
    if text:
        print("Analyzing content...")
        analysis = analyzer.analyze_content(text)
        
        print("\n📊 Content Analysis Results:")
        print(f"Title: {analysis['title']}")
        print(f"Year: {analysis['year']}")
        print(f"Themes: {', '.join(analysis['themes'])}")
        print(f"Key Quote: {analysis['key_quote']}")
        print(f"Analysis Method: {analysis['analysis_method']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate C.S. Lewis episode thumbnails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from text
  python thumbnail_cli.py --text "Lewis discusses medieval literature" --year 1936
  
  # Generate from image
  python thumbnail_cli.py --image book_page.jpg --year 1924
  
  # Interactive mode
  python thumbnail_cli.py --interactive
  
  # Just analyze content
  python thumbnail_cli.py --text "Some Lewis text..." --analyze-only
        """
    )
    
    parser.add_argument('--text', help='Text content to analyze')
    parser.add_argument('--image', help='Path to book page image')
    parser.add_argument('--year', help='Year for the episode content')
    parser.add_argument('--output', help='Custom output filename')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze content, don\'t generate thumbnail')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Analysis only mode
    if args.analyze_only:
        if not args.text and not args.image:
            print("Error: Need --text or --image for analysis")
            return
        analyze_content_only(args.text, args.image)
        return
    
    # Generate thumbnail
    if args.text:
        output_path = generate_from_text(args.text, args.year, args.output)
    elif args.image:
        output_path = generate_from_image(args.image, args.year, args.output)
    else:
        print("Error: Must provide either --text, --image, or --interactive")
        parser.print_help()
        return
    
    if output_path:
        print(f"✅ Thumbnail generated: {output_path}")
    else:
        print("❌ Failed to generate thumbnail")


if __name__ == "__main__":
    main()