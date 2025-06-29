"""Test YouTube caption scraping functionality."""

import sys
import os
import tempfile

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube.scraper import YouTubeScraper
from src.database.models import CaptionDatabase


def test_video_id_extraction():
    """Test video ID extraction from various URL formats."""
    print("🔍 Testing Video ID Extraction")
    print("=" * 40)
    
    scraper = YouTubeScraper()
    
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
    ]
    
    all_passed = True
    
    for url, expected in test_urls:
        result = scraper.extract_video_id(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} {url[:50]:<50} → {result}")
        if result != expected:
            all_passed = False
    
    return all_passed


def test_caption_parsing():
    """Test VTT caption parsing."""
    print("\n🎬 Testing Caption Parsing")
    print("=" * 40)
    
    scraper = YouTubeScraper()
    
    # Sample VTT content
    sample_vtt = """WEBVTT
Kind: captions
Language: en

00:00:01.000 --> 00:00:04.000
Welcome to this amazing video about

00:00:04.000 --> 00:00:08.000
the wonderful world of programming and technology.

00:00:08.000 --> 00:00:12.000
Today we'll explore some fascinating concepts.
"""
    
    captions = scraper.parse_vtt_captions(sample_vtt)
    
    if len(captions) == 3:
        print("✅ Parsed correct number of captions")
        
        # Check first caption
        first = captions[0]
        if (first['start_time'] == '00:00:01.000' and 
            first['end_time'] == '00:00:04.000' and
            'Welcome to this amazing video' in first['text']):
            print("✅ First caption parsed correctly")
            return True
        else:
            print("❌ First caption parsing failed")
            print(f"   Got: {first}")
            return False
    else:
        print(f"❌ Expected 3 captions, got {len(captions)}")
        return False


def test_database_operations():
    """Test database storage and retrieval."""
    print("\n💾 Testing Database Operations")
    print("=" * 40)
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        database = CaptionDatabase(db_path)
        print("✅ Database initialized")
        
        # Test data
        video_info = {
            'video_id': 'test123',
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'upload_date': '20231201',
            'duration': 300,
            'view_count': 1000
        }
        
        captions = [
            {'start_time': '00:00:01.000', 'end_time': '00:00:04.000', 'text': 'Hello world'},
            {'start_time': '00:00:04.000', 'end_time': '00:00:08.000', 'text': 'This is a test'},
            {'start_time': '00:00:08.000', 'end_time': '00:00:12.000', 'text': 'Programming is fun'}
        ]
        
        # Test storage
        success = database.store_video_data(video_info, captions)
        if success:
            print("✅ Video data stored successfully")
        else:
            print("❌ Failed to store video data")
            return False
        
        # Test retrieval
        retrieved_info = database.get_video_info('test123')
        if retrieved_info and retrieved_info['title'] == 'Test Video':
            print("✅ Video info retrieved successfully")
        else:
            print("❌ Failed to retrieve video info")
            return False
        
        retrieved_captions = database.get_video_captions('test123')
        if len(retrieved_captions) == 3:
            print("✅ Captions retrieved successfully")
        else:
            print(f"❌ Expected 3 captions, got {len(retrieved_captions)}")
            return False
        
        # Test search
        search_results = database.search_captions('programming')
        if len(search_results) > 0:
            print("✅ Caption search working")
        else:
            print("❌ Caption search failed")
            return False
        
        # Test statistics
        stats = database.get_statistics()
        if stats['video_count'] == 1 and stats['caption_count'] == 3:
            print("✅ Statistics working correctly")
        else:
            print(f"❌ Statistics incorrect: {stats}")
            return False
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_yt_dlp_availability():
    """Test if yt-dlp is available and working."""
    print("\n🛠️  Testing yt-dlp Availability")
    print("=" * 40)
    
    import subprocess
    
    try:
        # Test yt-dlp help command
        result = subprocess.run(['yt-dlp', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ yt-dlp is installed and accessible")
            
            # Try to get version
            version_result = subprocess.run(['yt-dlp', '--version'], 
                                          capture_output=True, text=True, timeout=5)
            if version_result.returncode == 0:
                version = version_result.stdout.strip()
                print(f"✅ yt-dlp version: {version}")
            
            return True
        else:
            print("❌ yt-dlp not working properly")
            return False
            
    except FileNotFoundError:
        print("❌ yt-dlp not found in PATH")
        print("   Install with: pip install yt-dlp")
        return False
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing yt-dlp: {e}")
        return False


def demonstrate_usage():
    """Show usage examples."""
    print("\n📖 Usage Examples")
    print("=" * 40)
    
    print("# Extract single video to file:")
    print('python extract_video.py "https://youtube.com/watch?v=VIDEO_ID" "output.txt"')
    print()
    
    print("# Scrape single video to database:")
    print('python youtube_cli.py video "https://youtube.com/watch?v=VIDEO_ID"')
    print()
    
    print("# Scrape entire channel:")
    print('python youtube_cli.py channel "https://youtube.com/@channelname"')
    print()
    
    print("# Search captions:")
    print('python youtube_cli.py search "your search term"')
    print()
    
    print("# Show database stats:")
    print('python youtube_cli.py stats')
    print()
    
    print("# Export video captions:")
    print('python youtube_cli.py export VIDEO_ID output.txt')


def main():
    """Run all YouTube scraping tests."""
    print("🎥 YouTube Caption Scraping Test Suite")
    print("=" * 50)
    
    tests = [
        ("Video ID Extraction", test_video_id_extraction),
        ("Caption Parsing", test_caption_parsing),
        ("Database Operations", test_database_operations),
        ("yt-dlp Availability", test_yt_dlp_availability),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if results.get("yt-dlp Availability", False):
        print("\n🚀 Ready to scrape YouTube captions!")
        demonstrate_usage()
    else:
        print("\n⚠️  Install yt-dlp to enable YouTube scraping:")
        print("   pip install yt-dlp")
    
    return all_passed


if __name__ == "__main__":
    main()