#!/usr/bin/env python3
"""
YouTube Caption Scraper CLI

This tool allows you to scrape captions from YouTube videos and channels,
store them in a database, and search through the content.

Usage Examples:
    # Scrape single video
    python youtube_cli.py video "https://youtube.com/watch?v=VIDEO_ID"
    
    # Scrape entire channel
    python youtube_cli.py channel "https://youtube.com/@channelname"
    
    # Search captions
    python youtube_cli.py search "medieval literature"
    
    # Export video captions to file
    python youtube_cli.py export VIDEO_ID output.txt
    
    # Show database statistics
    python youtube_cli.py stats
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.youtube.scraper import YouTubeScraper
from src.database.models import CaptionDatabase


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def scrape_video(video_url: str, db_path: str = "captions.db"):
    """Scrape captions from a single video."""
    print(f"🎬 Scraping video: {video_url}")
    
    scraper = YouTubeScraper()
    database = CaptionDatabase(db_path)
    
    # Extract video ID
    video_id = scraper.extract_video_id(video_url)
    if not video_id:
        print(f"❌ Could not extract video ID from: {video_url}")
        return False
    
    # Check if already exists
    if database.video_exists(video_id):
        print(f"ℹ️  Video {video_id} already exists in database")
        return True
    
    try:
        # Scrape video
        video_info, captions = scraper.get_video_captions(video_url)
        
        if not video_info or not captions:
            print(f"❌ No captions found for video: {video_url}")
            return False
        
        # Store in database
        success = database.store_video_data(video_info, captions)
        
        if success:
            print(f"✅ Successfully scraped '{video_info['title']}'")
            print(f"   - {len(captions)} caption segments")
            print(f"   - Duration: {video_info.get('duration', 'Unknown')} seconds")
            print(f"   - Uploader: {video_info.get('uploader', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to store video data")
            return False
            
    except Exception as e:
        print(f"❌ Error scraping video: {e}")
        return False


def scrape_channel(channel_url: str, max_videos: int = None, db_path: str = "captions.db"):
    """Scrape captions from entire channel."""
    print(f"📺 Scraping channel: {channel_url}")
    if max_videos:
        print(f"   - Limited to {max_videos} videos")
    
    scraper = YouTubeScraper()
    database = CaptionDatabase(db_path)
    
    try:
        # Get channel videos and scrape them
        results = scraper.scrape_channel(channel_url, max_videos)
        
        if not results:
            print(f"❌ No videos with captions found in channel")
            return False
        
        # Store all results in database
        success_count = 0
        
        for video_info, captions in results:
            if database.store_video_data(video_info, captions):
                success_count += 1
        
        print(f"✅ Channel scraping complete!")
        print(f"   - Successfully processed: {success_count}/{len(results)} videos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error scraping channel: {e}")
        return False


def search_captions(query: str, limit: int = 20, db_path: str = "captions.db"):
    """Search through stored captions."""
    print(f"🔍 Searching for: '{query}'")
    
    database = CaptionDatabase(db_path)
    
    try:
        results = database.search_captions(query, limit)
        
        if not results:
            print(f"❌ No results found for '{query}'")
            return
        
        print(f"✅ Found {len(results)} matches:")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']} ({result['uploader']})")
            print(f"   Video ID: {result['video_id']}")
            print(f"   Time: {result['start_time']} - {result['end_time']}")
            print(f"   Text: {result['text'][:200]}...")
            print(f"   URL: https://youtube.com/watch?v={result['video_id']}&t={result['start_time'][:2]}m{result['start_time'][3:5]}s")
        
    except Exception as e:
        print(f"❌ Error searching captions: {e}")


def export_video_captions(video_id: str, output_file: str, db_path: str = "captions.db"):
    """Export video captions to text file."""
    print(f"📄 Exporting captions for video: {video_id}")
    
    database = CaptionDatabase(db_path)
    
    try:
        success = database.export_video_captions(video_id, output_file)
        
        if success:
            print(f"✅ Captions exported to: {output_file}")
        else:
            print(f"❌ Failed to export captions for video: {video_id}")
            
    except Exception as e:
        print(f"❌ Error exporting captions: {e}")


def show_statistics(db_path: str = "captions.db"):
    """Show database statistics."""
    print("📊 Database Statistics")
    print("=" * 30)
    
    database = CaptionDatabase(db_path)
    
    try:
        stats = database.get_statistics()
        
        print(f"Videos: {stats.get('video_count', 0):,}")
        print(f"Caption segments: {stats.get('caption_count', 0):,}")
        print(f"Channels: {stats.get('channel_count', 0):,}")
        print(f"Last scraped: {stats.get('last_scraped', 'Never')}")
        
        db_size = stats.get('database_size', 0)
        if db_size > 0:
            if db_size > 1024 * 1024:
                size_str = f"{db_size / (1024 * 1024):.1f} MB"
            elif db_size > 1024:
                size_str = f"{db_size / 1024:.1f} KB"
            else:
                size_str = f"{db_size} bytes"
            print(f"Database size: {size_str}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def list_videos(channel_filter: str = None, db_path: str = "captions.db"):
    """List stored videos."""
    print("📋 Stored Videos")
    print("=" * 30)
    
    database = CaptionDatabase(db_path)
    
    try:
        if channel_filter:
            videos = database.get_channel_videos(channel_filter)
            print(f"Channel: {channel_filter}")
        else:
            # Get all videos (simplified query)
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT video_id, title, uploader, upload_date, caption_count
                    FROM videos 
                    ORDER BY upload_date DESC
                    LIMIT 50
                ''')
                videos = [dict(row) for row in cursor.fetchall()]
        
        if not videos:
            print("No videos found")
            return
        
        for video in videos:
            print(f"\n{video['title']}")
            print(f"  ID: {video['video_id']}")
            print(f"  Uploader: {video['uploader']}")
            print(f"  Date: {video['upload_date']}")
            print(f"  Captions: {video['caption_count']} segments")
        
    except Exception as e:
        print(f"❌ Error listing videos: {e}")


def extract_video_to_file(video_url: str, output_file: str):
    """Extract video captions directly to file (without database)."""
    print(f"📄 Extracting captions from: {video_url}")
    print(f"📁 Output file: {output_file}")
    
    scraper = YouTubeScraper()
    
    try:
        video_info, captions = scraper.get_video_captions(video_url)
        
        if not video_info or not captions:
            print(f"❌ No captions found for video")
            return False
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {video_info['title']}\n")
            f.write(f"Uploader: {video_info['uploader']}\n")
            f.write(f"Upload Date: {video_info['upload_date']}\n")
            f.write(f"Video ID: {video_info['video_id']}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write just the text content
            for caption in captions:
                f.write(f"{caption['text']}\n")
        
        print(f"✅ Extracted {len(captions)} caption segments")
        print(f"✅ Saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error extracting captions: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Caption Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape single video and store in database
  python youtube_cli.py video "https://youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Scrape channel (limit to 10 videos)
  python youtube_cli.py channel "https://youtube.com/@channelname" --max-videos 10
  
  # Search stored captions
  python youtube_cli.py search "medieval literature"
  
  # Export video captions to file
  python youtube_cli.py export dQw4w9WgXcQ output.txt
  
  # Extract video directly to file (no database)
  python youtube_cli.py extract "https://youtube.com/watch?v=dQw4w9WgXcQ" output.txt
  
  # Show database stats
  python youtube_cli.py stats
        """
    )
    
    parser.add_argument('--db', default='captions.db', help='Database file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Video command
    video_parser = subparsers.add_parser('video', help='Scrape single video')
    video_parser.add_argument('url', help='Video URL')
    
    # Channel command
    channel_parser = subparsers.add_parser('channel', help='Scrape entire channel')
    channel_parser.add_argument('url', help='Channel URL')
    channel_parser.add_argument('--max-videos', type=int, help='Maximum videos to process')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search captions')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=20, help='Maximum results')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export video captions')
    export_parser.add_argument('video_id', help='Video ID')
    export_parser.add_argument('output', help='Output file path')
    
    # Extract command (direct to file)
    extract_parser = subparsers.add_parser('extract', help='Extract video to file (no database)')
    extract_parser.add_argument('url', help='Video URL')
    extract_parser.add_argument('output', help='Output file path')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List stored videos')
    list_parser.add_argument('--channel', help='Filter by channel ID')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'video':
        scrape_video(args.url, args.db)
    
    elif args.command == 'channel':
        scrape_channel(args.url, args.max_videos, args.db)
    
    elif args.command == 'search':
        search_captions(args.query, args.limit, args.db)
    
    elif args.command == 'export':
        export_video_captions(args.video_id, args.output, args.db)
    
    elif args.command == 'extract':
        extract_video_to_file(args.url, args.output)
    
    elif args.command == 'stats':
        show_statistics(args.db)
    
    elif args.command == 'list':
        list_videos(args.channel, args.db)


if __name__ == "__main__":
    main()