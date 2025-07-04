# Claude YouTube Scraping Instructions

## ⚠️ CRITICAL WARNING
**Before starting any YouTube scraping project, READ SECTION 6 for mandatory implementation requirements. Using incorrect yt-dlp parameters results in 90%+ failure rates.**

## Overview
These are the exact steps Claude should follow to scrape YouTube videos and add them to a captions database, based on the workflow used in the Sserf project. This includes the mandatory 4-criteria thumbnail text extraction protocol and critical fixes to avoid common failures.

## Prerequisites Setup

### 1. Required Dependencies
Ensure these are installed in the project:
```bash
pip install yt-dlp requests pillow sqlite3
```

### 2. Project Structure Expected
```
project/
├── src/
│   ├── youtube/
│   │   └── scraper.py
│   └── database/
│       └── models.py
├── youtube_cli.py
├── captions_backup.db (or similar database file)
└── requirements.txt
```

### 3. Key Files to Check
- `youtube_cli.py` - Main scraping interface
- `src/youtube/scraper.py` - Core scraping functionality  
- `src/database/models.py` - Database operations
- Existing database file (usually `captions_backup.db` or `captions.db`)

### 4. Critical Implementation Requirements

**⚠️ IMPORTANT**: To avoid common scraping failures (like achieving only 8% success rate), ensure these fixes are implemented from the start:

**Required yt-dlp Parameters:**
- Use `--write-auto-subs` (gets auto-generated captions) 
- Use `--sub-langs 'en.*'` (all English variants, not just 'en')
- Include rate limiting: `--sleep-interval` and `--max-sleep-interval`
- Implement batch processing with delays between requests

**Do NOT use these problematic parameters:**
- ❌ `--write-subs` only (misses auto-generated captions)
- ❌ `--sub-lang 'en'` (too restrictive, misses variants)
- ❌ No rate limiting (causes YouTube 429 errors)

## Step-by-Step YouTube Scraping Workflow

### Phase 1: Pre-Scraping Analysis

**1. Check Current Database Status**
```bash
python3 youtube_cli.py --db [database_file] stats
```
**Purpose**: Understand current content and get baseline numbers

**Expected Output**: 
- Current video count
- Caption segment count  
- Database size
- Last scraped date

**2. Identify Target Channel**
- Find the YouTube channel URL (format: `https://www.youtube.com/channel/[CHANNEL_ID]` or `https://www.youtube.com/@[USERNAME]`)
- Note channel name for reference

**3. Check for Missing Videos (if updating existing database)**
Use this process to find videos not yet in the database:
```bash
# Get all channel video IDs
yt-dlp --flat-playlist --dump-json "[CHANNEL_URL]" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 > channel_videos.txt

# Compare with database (requires database query)
# Create targeted list of missing videos
```

### Phase 2: Scraping Execution

**⚠️ CRITICAL**: Before running these commands, verify that `src/youtube/scraper.py` uses the correct parameters (see Section 6 below).

**Method A: Test with Small Batch First (RECOMMENDED)**
```bash
python3 youtube_cli.py --db [database_file] channel "[CHANNEL_URL]" --max-videos 10
```
**Purpose**: Verify scraping works correctly before processing entire channel.

**Method B: Scrape Entire Channel (After successful test)**
```bash
python3 youtube_cli.py --db [database_file] channel "[CHANNEL_URL]"
```

**Method C: Scrape Specific Videos**
```bash
python3 youtube_cli.py --db [database_file] video "[VIDEO_URL]"
```

**Method D: Resume Incomplete Scraping**
```bash
python3 youtube_cli.py --db [database_file] resume "[CHANNEL_URL]"
```
**Purpose**: Continue scraping videos that failed or were missed in previous runs.

### Phase 3: Monitor Scraping Progress

**Expected Behavior During Scraping:**
- Tool will show progress: "Processing video X/Y"
- Each video shows extraction count: "Extracted N caption segments"  
- Success messages: "✅ Successfully scraped: [VIDEO_TITLE]"
- Warning messages: "⚠️ No captions found for: [VIDEO_URL]" (this is normal)

**Handle Common Issues:**
- **No captions available**: Normal for some videos, tool will continue
- **Rate limiting**: Tool handles this automatically
- **Network errors**: Tool will retry and continue
- **Long processing time**: Normal for channels with many videos

### Phase 4: Critical Thumbnail Text Extraction Protocol

**MANDATORY for ALL newly scraped videos**: Follow the 4-criteria protocol exactly as documented in the project's CLAUDE.md:

**For Each New Video:**

1. **✅ Criterion 1: Individual Claude Vision Reading**
   - Get the thumbnail URL from the video metadata
   - Download the thumbnail image
   - Use Claude's vision capabilities to read the thumbnail text
   - DO NOT use automated OCR or text detection tools

2. **✅ Criterion 2: Extract Exact Text**
   - Read all visible text in the thumbnail
   - Note fonts, colors, positioning if relevant
   - Capture exact spelling and punctuation
   - Include episode numbers, dates, titles, etc.

3. **✅ Criterion 3: Database Update**
   - Update the `thumbnail_text` field in the database
   - Use proper SQL UPDATE commands
   - Verify the text was stored correctly

4. **✅ Criterion 4: Repository Documentation**
   - Document the extraction in a log file
   - Include this in any repository commits
   - Follow project-specific commit message format

### Phase 5: Verification and Quality Control

**1. Verify Database Updates**
```bash
python3 youtube_cli.py --db [database_file] stats
```
Compare before/after numbers to confirm new content was added.

**2. Test Search Functionality**
```bash
python3 youtube_cli.py --db [database_file] search "test query"
```
Verify new content is searchable.

**3. Check for Failed Videos**
Review scraping logs for videos that failed to process and determine if action is needed.

## Detailed Command Examples

### Single Video Scraping
```bash
# Scrape one specific video
python3 youtube_cli.py --db captions_backup.db video "https://www.youtube.com/watch?v=VIDEO_ID"

# Expected output:
# 🎬 Scraping video: https://www.youtube.com/watch?v=VIDEO_ID
# ✅ Successfully scraped 'Video Title'
#    - 500 caption segments
#    - Duration: 1800 seconds
#    - Uploader: Channel Name
```

### Channel Scraping
```bash
# Scrape entire channel
python3 youtube_cli.py --db captions_backup.db channel "https://www.youtube.com/@channelname"

# Limited scraping (first 20 videos)
python3 youtube_cli.py --db captions_backup.db channel "https://www.youtube.com/@channelname" --max-videos 20
```

### Database Management
```bash
# Check stats
python3 youtube_cli.py --db captions_backup.db stats

# Search content
python3 youtube_cli.py --db captions_backup.db search "search term"

# List videos
python3 youtube_cli.py --db captions_backup.db list

# Export specific video
python3 youtube_cli.py --db captions_backup.db export VIDEO_ID output.txt
```

## Section 6: Critical scraper.py Implementation

**⚠️ MANDATORY**: Use this exact implementation to avoid 90%+ failure rates.

### Correct download_captions Method:
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

### Required: Rate-Limited Channel Scraping
Add this method to YouTubeScraper class:
```python
def scrape_channel_with_rate_limiting(self, channel_url: str, max_videos: Optional[int] = None):
    """Scrape channel with proper rate limiting to avoid 429 errors."""
    import time
    import random
    
    video_urls = self.get_channel_videos(channel_url, max_videos)
    if not video_urls:
        return []
    
    results = []
    batch_size = 10
    
    for i in range(0, len(video_urls), batch_size):
        batch = video_urls[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}")
        
        for j, video_url in enumerate(batch):
            if j > 0:  # Add delays between videos
                delay = 2 + random.uniform(0, 2)
                time.sleep(delay)
            
            try:
                video_info, captions = self.get_video_captions(video_url)
                if video_info:
                    results.append((video_info, captions or []))
            except Exception as e:
                logger.error(f"Error processing {video_url}: {e}")
                time.sleep(5)  # Longer delay after errors
        
        # Delay between batches
        if i + batch_size < len(video_urls):
            time.sleep(10)
    
    return results
```

## Thumbnail Text Extraction Code Pattern

```python
# Example of thumbnail text extraction process
import requests
from PIL import Image
import sqlite3

def extract_thumbnail_text_for_video(video_id, database_path):
    """Extract thumbnail text using Claude vision and update database"""
    
    # 1. Get thumbnail URL from database or video metadata
    thumbnail_url = get_thumbnail_url(video_id)
    
    # 2. Download thumbnail image
    response = requests.get(thumbnail_url)
    with open(f"thumbnail_{video_id}.jpg", "wb") as f:
        f.write(response.content)
    
    # 3. Use Claude vision to read text (this step requires manual Claude interaction)
    print(f"Please use Claude vision to read text from thumbnail_{video_id}.jpg")
    extracted_text = input("Enter extracted text: ")
    
    # 4. Update database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE videos SET thumbnail_text = ? WHERE video_id = ?", 
        (extracted_text, video_id)
    )
    conn.commit()
    conn.close()
    
    print(f"✅ Updated thumbnail text for {video_id}: {extracted_text}")
```

## Error Handling and Troubleshooting

### Common Issues and Solutions

**1. LOW SUCCESS RATE (8-15% videos scraped successfully)**
**Problem**: Using `--write-subs` only and `--sub-lang 'en'`
**Solution**: Use the exact code from Section 6 above with `--write-auto-subs` and `--sub-langs 'en.*'`

**2. YouTube 429 Rate Limiting Errors**
**Problem**: No delays between requests, processing too aggressively
**Solution**: Implement the rate-limited scraping method from Section 6

**3. "No captions found" for 90%+ of videos**
**Problem**: Missing auto-generated captions (most common type)
**Solution**: Ensure `--write-auto-subs` is included in yt-dlp command

**4. VTT File Detection Failures**
**Problem**: Looking for exact filename matches
**Solution**: Use pattern matching for files containing 'en' or 'auto' in filename

**5. Database Connection Errors**
- Verify database file exists and is accessible
- Check file permissions
- Ensure database path is correct

**6. yt-dlp Errors**
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check if video/channel is accessible
- Verify URL format is correct

### Recovery Procedures

**Resume Interrupted Scraping:**
- The tool automatically skips videos already in database
- Re-run the same command to continue where left off

**Database Corruption:**
- Keep regular backups before major scraping operations
- Use database verification commands to check integrity

## Repository Update Workflow

After successful scraping, follow these steps:

**1. Verify Results**
```bash
python3 youtube_cli.py --db [database_file] stats
```

**2. Create Database Backup**
```bash
cp [database_file] [database_file]_backup_$(date +%Y%m%d)
```

**3. Compress Database for Repository**
```bash
gzip -c [database_file] > [database_file].gz
```

**4. Update Repository**
```bash
git add [database_file].gz
git add [other_modified_files]
git commit -m "Scraped X new videos from [channel_name] - Added Y caption segments"
git push origin main
```

## Quality Assurance Checklist

Before considering scraping complete:

- [ ] **Success rate >80%** - If below 80%, implement Section 6 fixes
- [ ] Database stats show expected increase in videos/captions
- [ ] Search functionality tested with new content
- [ ] All new videos processed through 4-criteria thumbnail protocol
- [ ] Failed videos documented and explained (should be <20%)
- [ ] No persistent 429 rate limiting errors
- [ ] Database backed up and added to repository
- [ ] Project documentation updated if needed

**Success Rate Benchmarks:**
- **>90%** = Excellent (using proper auto-caption support)
- **80-90%** = Good (some videos legitimately have no captions)
- **50-80%** = Poor (missing auto-captions, implement Section 6 fixes)
- **<50%** = Critical failure (wrong yt-dlp parameters, fix immediately)

## Integration Notes

**For New Projects:**
1. Copy the core scraping files (`youtube_cli.py`, `src/youtube/`, `src/database/`)
2. Install required dependencies
3. Adapt database schema if needed
4. Follow the same 4-criteria thumbnail protocol
5. Maintain the same command-line interface for consistency

**Channel-Specific Considerations:**
- Some channels may have different caption availability
- Adjust scraping parameters based on channel size
- Consider rate limiting for very large channels
- Document channel-specific quirks or issues

This workflow ensures consistent, high-quality YouTube scraping with proper database management and search functionality across different projects.