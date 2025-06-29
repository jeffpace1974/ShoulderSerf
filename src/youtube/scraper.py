"""YouTube caption scraping functionality using yt-dlp."""

import logging
import re
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import requests


logger = logging.getLogger(__name__)


class YouTubeScraper:
    """YouTube caption scraper using yt-dlp."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch.*?v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If URL is already just an ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    def extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from YouTube URL."""
        patterns = [
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/user/([^/?]+)',
            r'youtube\.com/@([^/?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_url: str) -> Dict:
        """Get video metadata using yt-dlp."""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            video_info = json.loads(result.stdout)
            
            return {
                'video_id': video_info.get('id'),
                'title': video_info.get('title'),
                'uploader': video_info.get('uploader'),
                'upload_date': video_info.get('upload_date'),
                'duration': video_info.get('duration'),
                'view_count': video_info.get('view_count'),
                'description': video_info.get('description', ''),
                'thumbnail': video_info.get('thumbnail'),
                'channel_id': video_info.get('channel_id'),
                'channel_url': video_info.get('channel_url')
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get video info: {e.stderr}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse video info JSON: {e}")
            return {}
    
    def download_captions(self, video_url: str, lang: str = 'en') -> Optional[str]:
        """Download captions for a video using yt-dlp."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                cmd = [
                    'yt-dlp',
                    '--write-subs',
                    '--write-auto-subs',
                    '--sub-lang', lang,
                    '--sub-format', 'vtt',
                    '--skip-download',
                    '--output', os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    video_url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Find the downloaded VTT file
                vtt_files = [f for f in os.listdir(temp_dir) if f.endswith('.vtt')]
                
                if vtt_files:
                    vtt_path = os.path.join(temp_dir, vtt_files[0])
                    with open(vtt_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    logger.warning(f"No captions found for video: {video_url}")
                    return None
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download captions: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Error downloading captions: {e}")
            return None
    
    def parse_vtt_captions(self, vtt_content: str) -> List[Dict]:
        """Parse VTT caption content into structured data."""
        if not vtt_content:
            return []
        
        captions = []
        lines = vtt_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip header and empty lines
            if line.startswith('WEBVTT') or line.startswith('NOTE') or not line:
                i += 1
                continue
            
            # Look for timestamp line
            if '-->' in line:
                timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
                if timestamp_match:
                    start_time = timestamp_match.group(1)
                    end_time = timestamp_match.group(2)
                    
                    # Collect caption text (may span multiple lines)
                    i += 1
                    caption_text = []
                    
                    while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                        text = lines[i].strip()
                        # Remove VTT formatting tags
                        text = re.sub(r'<[^>]+>', '', text)
                        if text:
                            caption_text.append(text)
                        i += 1
                    
                    if caption_text:
                        captions.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': ' '.join(caption_text)
                        })
                else:
                    i += 1
            else:
                i += 1
        
        return captions
    
    def get_video_captions(self, video_url: str, lang: str = 'en') -> Tuple[Dict, List[Dict]]:
        """Get complete video information and captions."""
        logger.info(f"Scraping video: {video_url}")
        
        # Get video metadata
        video_info = self.get_video_info(video_url)
        
        if not video_info:
            logger.error(f"Failed to get video info for: {video_url}")
            return {}, []
        
        # Download and parse captions
        vtt_content = self.download_captions(video_url, lang)
        captions = self.parse_vtt_captions(vtt_content) if vtt_content else []
        
        logger.info(f"Extracted {len(captions)} caption segments from '{video_info.get('title', 'Unknown')}'")
        
        return video_info, captions
    
    def get_channel_videos(self, channel_url: str, max_videos: Optional[int] = None) -> List[str]:
        """Get list of video URLs from a channel."""
        try:
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--dump-json'
            ]
            
            if max_videos and max_videos > 0:
                cmd.extend(['--playlist-end', str(max_videos)])
            
            cmd.append(channel_url)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            video_urls = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_info = json.loads(line)
                        if video_info.get('id'):
                            video_urls.append(f"https://www.youtube.com/watch?v={video_info['id']}")
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"Found {len(video_urls)} videos in channel")
            return video_urls
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get channel videos: {e.stderr}")
            return []
    
    def scrape_channel(self, channel_url: str, max_videos: Optional[int] = None, lang: str = 'en') -> List[Tuple[Dict, List[Dict]]]:
        """Scrape captions from all videos in a channel."""
        logger.info(f"Scraping channel: {channel_url}")
        
        video_urls = self.get_channel_videos(channel_url, max_videos)
        
        if not video_urls:
            logger.error("No videos found in channel")
            return []
        
        results = []
        
        for i, video_url in enumerate(video_urls, 1):
            logger.info(f"Processing video {i}/{len(video_urls)}: {video_url}")
            
            try:
                video_info, captions = self.get_video_captions(video_url, lang)
                
                if video_info and captions:
                    results.append((video_info, captions))
                    logger.info(f"✅ Successfully scraped: {video_info.get('title', 'Unknown')}")
                else:
                    logger.warning(f"⚠️  No captions found for: {video_url}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {video_url}: {e}")
                continue
        
        logger.info(f"Completed channel scraping. Successfully processed {len(results)}/{len(video_urls)} videos")
        return results
    
    def extract_captions_text(self, captions: List[Dict]) -> str:
        """Extract plain text from caption segments."""
        return ' '.join([caption['text'] for caption in captions])
    
    def search_captions(self, captions: List[Dict], query: str, context_words: int = 10) -> List[Dict]:
        """Search for query within captions and return matches with context."""
        query_lower = query.lower()
        matches = []
        
        for i, caption in enumerate(captions):
            if query_lower in caption['text'].lower():
                # Get surrounding context
                start_idx = max(0, i - context_words)
                end_idx = min(len(captions), i + context_words + 1)
                
                context_captions = captions[start_idx:end_idx]
                context_text = ' '.join([c['text'] for c in context_captions])
                
                matches.append({
                    'match_caption': caption,
                    'context': context_text,
                    'start_time': caption['start_time'],
                    'end_time': caption['end_time']
                })
        
        return matches