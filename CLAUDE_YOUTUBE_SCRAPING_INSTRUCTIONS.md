# Claude YouTube Scraping Instructions

## Overview
These are the exact steps Claude should follow to scrape YouTube videos and add them to a captions database, based on the workflow used in the Sserf project. This includes the mandatory 4-criteria thumbnail text extraction protocol.

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

**Method A: Scrape Entire Channel**
```bash
python3 youtube_cli.py --db [database_file] channel "[CHANNEL_URL]"
```

**Method B: Scrape Specific Videos**
```bash
python3 youtube_cli.py --db [database_file] video "[VIDEO_URL]"
```

**Method C: Limited Channel Scrape (for testing)**
```bash
python3 youtube_cli.py --db [database_file] channel "[CHANNEL_URL]" --max-videos 10
```

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

**1. "No captions found" Warnings**
- This is normal - not all videos have captions
- Tool will continue processing other videos
- Videos without captions are still added to database for completeness

**2. Database Connection Errors**
- Verify database file exists and is accessible
- Check file permissions
- Ensure database path is correct

**3. yt-dlp Errors**
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check if video/channel is accessible
- Verify URL format is correct

**4. Rate Limiting**
- Tool handles this automatically
- If persistent issues, add delays between requests
- Consider processing in smaller batches

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

- [ ] Database stats show expected increase in videos/captions
- [ ] Search functionality tested with new content
- [ ] All new videos processed through 4-criteria thumbnail protocol
- [ ] Failed videos documented and explained
- [ ] Database backed up and added to repository
- [ ] Project documentation updated if needed

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