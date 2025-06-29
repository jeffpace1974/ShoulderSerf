#!/usr/bin/env python3
"""
Simple video caption extractor - extracts captions from a single YouTube video to a text file.

Usage:
    python extract_video.py "VIDEO_URL" "output.txt"
    
Examples:
    python extract_video.py "https://youtube.com/watch?v=dQw4w9WgXcQ" "video_captions.txt"
    python extract_video.py "dQw4w9WgXcQ" "output.txt"
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.youtube.scraper import YouTubeScraper


def main():
    """Extract captions from a single video to text file."""
    
    if len(sys.argv) != 3:
        print("Usage: python extract_video.py VIDEO_URL OUTPUT_FILE")
        print("")
        print("Examples:")
        print('  python extract_video.py "https://youtube.com/watch?v=dQw4w9WgXcQ" "captions.txt"')
        print('  python extract_video.py "dQw4w9WgXcQ" "output.txt"')
        sys.exit(1)
    
    video_url = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"🎬 Extracting captions from: {video_url}")
    print(f"📄 Output file: {output_file}")
    
    scraper = YouTubeScraper()
    
    try:
        # Get video info and captions
        video_info, captions = scraper.get_video_captions(video_url)
        
        if not video_info:
            print("❌ Could not get video information")
            sys.exit(1)
        
        if not captions:
            print("❌ No captions found for this video")
            sys.exit(1)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"Title: {video_info.get('title', 'Unknown')}\n")
            f.write(f"Uploader: {video_info.get('uploader', 'Unknown')}\n")
            f.write(f"Upload Date: {video_info.get('upload_date', 'Unknown')}\n")
            f.write(f"Duration: {video_info.get('duration', 'Unknown')} seconds\n")
            f.write(f"Video ID: {video_info.get('video_id', 'Unknown')}\n")
            f.write(f"URL: https://youtube.com/watch?v={video_info.get('video_id', '')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write captions (just the text)
            for caption in captions:
                f.write(f"{caption['text']}\n")
        
        print(f"✅ Successfully extracted {len(captions)} caption segments")
        print(f"✅ Video: {video_info.get('title', 'Unknown')}")
        print(f"✅ Saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()