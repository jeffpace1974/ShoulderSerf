#!/usr/bin/env python3
"""
Quick validation script - tests just the thumbnail generation without dependencies.
Run this first to verify basic functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def quick_thumbnail_test():
    """Quick test of thumbnail generation functionality."""
    print("🎨 Quick Thumbnail Test")
    print("=" * 30)
    
    try:
        from src.thumbnail.generator import ThumbnailGenerator
        
        # Create generator
        generator = ThumbnailGenerator()
        print("✅ ThumbnailGenerator initialized")
        
        # Test basic generation
        print("\n📝 Testing basic thumbnail...")
        output_path = generator.generate_thumbnail(
            title="Lewis Discusses Medieval Tales",
            year="1935",
            output_filename="quick_test.png"
        )
        
        if output_path and os.path.exists(output_path):
            print(f"✅ Basic thumbnail created: {output_path}")
            
            # Test content analysis (without AI)
            print("\n🧠 Testing content analysis...")
            test_text = """
            Today I had quite the debate with a colleague about Tom Jones. 
            He thinks Fielding's novel is mere entertainment, but I believe 
            there's genuine moral instruction woven throughout. Sometimes 
            a good story teaches us more about human nature than the most 
            serious philosophical treatise. This was during our lunch break 
            in 1941 at Oxford.
            """
            
            from src.thumbnail.content_analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer()
            analysis = analyzer.analyze_content(test_text)
            
            print(f"Generated Title: '{analysis['title']}'")
            print(f"Detected Year: {analysis['year']}")
            print(f"Themes: {', '.join(analysis['themes'])}")
            
            # Generate thumbnail from content
            content_output = generator.generate_from_content(test_text, year="1941")
            
            if content_output and os.path.exists(content_output):
                print(f"✅ Content-based thumbnail created: {content_output}")
                
                print("\n🎉 SUCCESS! Basic thumbnail system is working.")
                print("\nGenerated files:")
                print(f"  - {output_path}")
                print(f"  - {content_output}")
                print("\nNext steps:")
                print("  1. Run: python test_system.py  (full system test)")
                print("  2. Try: python thumbnail_cli.py --interactive")
                
                return True
            else:
                print("❌ Content-based generation failed")
                return False
        else:
            print("❌ Basic thumbnail generation failed")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_thumbnail_test()
    
    if not success:
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the Sserf directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check Python version: python --version (need 3.8+)")
        sys.exit(1)
    else:
        sys.exit(0)