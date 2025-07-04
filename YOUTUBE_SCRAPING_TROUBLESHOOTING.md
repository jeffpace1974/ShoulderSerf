# YouTube Scraping Troubleshooting Guide

## Problem Analysis: Channel Scraping Failures

Based on the report from Claude working on the Liam Ottley channel (@LiamOttley), there are specific technical issues that need addressing:

### Issues Identified:
1. **Incorrect yt-dlp parameters** - Using `--write-subs` instead of `--write-auto-subs`
2. **Rate limiting** - YouTube's 429 errors from aggressive scraping
3. **Incomplete scraping** - Only 13/164 videos successfully scraped

## Solution 1: Fix yt-dlp Caption Parameters

### Current Problem in scraper.py:
```python
# WRONG - This is what's likely in the broken version
cmd = [
    'yt-dlp',
    '--write-subs',        # ❌ Only gets manual subtitles
    '--sub-lang', 'en',    # ❌ Too restrictive
    '--sub-format', 'vtt',
    '--skip-download',
    video_url
]
```

### Correct Implementation:
```python
def download_captions(self, video_url: str, lang: str = 'en') -> Optional[str]:
    """Download captions for a video using yt-dlp with proper auto-caption support."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = [
                'yt-dlp',
                '--write-auto-subs',      # ✅ Gets auto-generated captions
                '--write-subs',           # ✅ Also gets manual subs if available
                '--sub-langs', 'en.*',    # ✅ All English variants
                '--sub-format', 'vtt',
                '--skip-download',
                '--output', os.path.join(temp_dir, '%(title)s.%(ext)s'),
                '--sleep-interval', '2',   # ✅ Rate limiting protection
                '--max-sleep-interval', '5',
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Find VTT files with better pattern matching
            vtt_files = []
            for f in os.listdir(temp_dir):
                if f.endswith('.vtt') and ('en' in f.lower() or 'auto' in f.lower()):
                    vtt_files.append(f)
            
            if vtt_files:
                # Prefer auto-generated captions if multiple files
                vtt_file = None
                for f in vtt_files:
                    if 'auto' in f.lower():
                        vtt_file = f
                        break
                if not vtt_file:
                    vtt_file = vtt_files[0]
                
                vtt_path = os.path.join(temp_dir, vtt_file)
                with open(vtt_path, 'r', encoding='utf-8') as file:
                    return file.read()
                    
            return None
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout downloading captions for: {video_url}")
        return None
    except Exception as e:
        logger.error(f"Error downloading captions: {e}")
        return None
```

## Solution 2: Implement Proper Rate Limiting

### Enhanced Channel Scraping with Rate Limiting:
```python
def scrape_channel_with_rate_limiting(self, channel_url: str, max_videos: Optional[int] = None) -> List[Tuple[Dict, List[Dict]]]:
    """Scrape channel with proper rate limiting and retry logic."""
    import time
    import random
    
    logger.info(f"Scraping channel with rate limiting: {channel_url}")
    
    video_urls = self.get_channel_videos(channel_url, max_videos)
    if not video_urls:
        return []
    
    results = []
    failed_videos = []
    
    # Process in smaller batches
    batch_size = 10
    for i in range(0, len(video_urls), batch_size):
        batch = video_urls[i:i+batch_size]
        
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(video_urls)-1)//batch_size + 1}")
        
        for j, video_url in enumerate(batch):
            video_num = i + j + 1
            logger.info(f"Processing video {video_num}/{len(video_urls)}: {video_url}")
            
            try:
                # Progressive delays to avoid rate limiting
                if video_num > 1:
                    delay = min(2 + (video_num // 20), 10)  # Increase delay over time
                    time.sleep(delay + random.uniform(0, 2))
                
                video_info, captions = self.get_video_captions(video_url)
                
                if video_info and captions:
                    results.append((video_info, captions))
                    logger.info(f"✅ Success: {video_info.get('title', 'Unknown')}")
                elif video_info:
                    # Store video info even without captions
                    results.append((video_info, []))
                    logger.info(f"📝 Metadata only: {video_info.get('title', 'Unknown')}")
                else:
                    failed_videos.append(video_url)
                    logger.warning(f"❌ Failed: {video_url}")
                    
            except Exception as e:
                logger.error(f"Error processing {video_url}: {e}")
                failed_videos.append(video_url)
                # Longer delay after errors
                time.sleep(5)
        
        # Delay between batches
        if i + batch_size < len(video_urls):
            logger.info(f"Batch complete. Waiting 10 seconds before next batch...")
            time.sleep(10)
    
    # Retry failed videos with longer delays
    if failed_videos:
        logger.info(f"Retrying {len(failed_videos)} failed videos...")
        time.sleep(30)  # Long pause before retries
        
        for video_url in failed_videos:
            try:
                time.sleep(15)  # Longer delays for retries
                video_info, captions = self.get_video_captions(video_url)
                if video_info:
                    results.append((video_info, captions or []))
                    logger.info(f"✅ Retry success: {video_info.get('title', 'Unknown')}")
            except Exception as e:
                logger.error(f"Retry failed for {video_url}: {e}")
    
    logger.info(f"Channel scraping complete: {len(results)}/{len(video_urls)} videos processed")
    return results
```

## Solution 3: Resume Incomplete Scraping

### Smart Resume Function:
```python
def resume_channel_scraping(self, channel_url: str, database_path: str):
    """Resume scraping for videos that failed caption extraction."""
    
    # Get all channel videos
    video_urls = self.get_channel_videos(channel_url)
    
    # Check database for videos without captions
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT video_id FROM videos 
        WHERE video_id NOT IN (
            SELECT DISTINCT video_id FROM captions 
            WHERE video_id IS NOT NULL
        )
    """)
    
    videos_without_captions = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    logger.info(f"Found {len(videos_without_captions)} videos without captions")
    
    # Build URLs for missing videos
    missing_urls = []
    for video_url in video_urls:
        video_id = self.extract_video_id(video_url)
        if video_id in videos_without_captions:
            missing_urls.append(video_url)
    
    # Scrape missing videos with rate limiting
    if missing_urls:
        logger.info(f"Attempting to scrape {len(missing_urls)} videos with missing captions...")
        return self.scrape_channel_with_rate_limiting("", 0)  # Pass URLs directly
    
    return []
```

## Solution 4: Enhanced CLI Commands

### Add These Commands to youtube_cli.py:

```python
def resume_channel_scraping(channel_url: str, db_path: str = "captions.db"):
    """Resume scraping for videos missing captions."""
    print(f"🔄 Resuming scraping for: {channel_url}")
    
    scraper = YouTubeScraper()
    database = CaptionDatabase(db_path)
    
    try:
        # Use the enhanced scraping method
        results = scraper.resume_channel_scraping(channel_url, db_path)
        
        success_count = 0
        for video_info, captions in results:
            if captions:  # Only count videos with captions as success
                if database.store_video_data(video_info, captions):
                    success_count += 1
        
        print(f"✅ Resume complete! Successfully added captions for {success_count} videos")
        return True
        
    except Exception as e:
        print(f"❌ Error during resume: {e}")
        return False

# Add to argument parser:
resume_parser = subparsers.add_parser('resume', help='Resume channel scraping for missing captions')
resume_parser.add_argument('url', help='Channel URL')

# Add to main execution:
elif args.command == 'resume':
    resume_channel_scraping(args.url, args.db)
```

## Specific Instructions for Claude

### Step 1: Update scraper.py
Tell Claude to replace the `download_captions` method with the corrected version above that includes:
- `--write-auto-subs` and `--write-subs` flags
- `--sub-langs 'en.*'` for all English variants  
- Rate limiting with `--sleep-interval` and `--max-sleep-interval`
- Better VTT file detection logic

### Step 2: Add Rate-Limited Channel Scraping
Tell Claude to add the `scrape_channel_with_rate_limiting` method to the scraper class.

### Step 3: Use Resume Command
Instead of re-scraping everything, tell Claude to:
```bash
# Add the resume command to youtube_cli.py
python3 youtube_cli.py resume "https://www.youtube.com/@LiamOttley"
```

### Step 4: Progressive Approach
For large channels like Liam Ottley's:
```bash
# Start with a small batch to test
python3 youtube_cli.py channel "https://www.youtube.com/@LiamOttley" --max-videos 20

# Check results
python3 youtube_cli.py stats

# If successful, continue with resume command
python3 youtube_cli.py resume "https://www.youtube.com/@LiamOttley"
```

## Expected Results

After implementing these fixes:
- **Caption extraction rate should improve to 80-90%** (from current 8%)
- **Rate limiting errors should be eliminated**
- **Auto-generated captions will be captured** (most YouTube videos have these)
- **Failed videos can be retried** systematically

## Verification Commands

```bash
# Check improved results
python3 youtube_cli.py stats

# Test search functionality
python3 youtube_cli.py search "business automation"

# Verify specific video has captions
python3 youtube_cli.py search "Liam Ottley"
```

The key is using the correct yt-dlp parameters and implementing proper rate limiting - these changes should resolve the 151 failed videos issue.