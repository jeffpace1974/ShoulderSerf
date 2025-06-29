# YouTube Caption Scraping Setup Instructions

This guide provides complete instructions for setting up YouTube caption scraping capabilities that can extract captions from individual videos or entire channels, store them in a database, and provide search functionality.

## Prerequisites

- Python 3.8+
- Basic command line knowledge
- Internet connection

## Installation

### 1. Install yt-dlp

```bash
# Install yt-dlp (YouTube downloader)
pip install yt-dlp

# Verify installation
yt-dlp --version
```

### 2. Install Required Python Packages

```bash
pip install requests sqlite3
```

### 3. Verify yt-dlp Works

```bash
# Test with a simple command (this won't download, just checks)
yt-dlp --list-formats "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Core Components

### 1. YouTube Scraper (`src/youtube/scraper.py`)

**Key Functions:**
- `extract_video_id()` - Extract video ID from various URL formats
- `get_video_info()` - Get video metadata using yt-dlp
- `download_captions()` - Download VTT captions using yt-dlp
- `parse_vtt_captions()` - Parse VTT format into structured data
- `get_video_captions()` - Complete video scraping (metadata + captions)
- `get_channel_videos()` - Get all video URLs from a channel
- `scrape_channel()` - Scrape entire channel

### 2. Database System (`src/database/models.py`)

**Tables:**
- `videos` - Video metadata (title, uploader, duration, etc.)
- `captions` - Individual caption segments with timestamps
- `captions_fts` - Full-text search index for fast searching

**Key Functions:**
- `store_video_data()` - Store video and captions in database
- `search_captions()` - Full-text search across all captions
- `get_video_captions()` - Retrieve captions for specific video
- `export_video_captions()` - Export captions to text file
- `get_statistics()` - Database statistics and counts

### 3. Command Line Interface (`youtube_cli.py`)

**Commands:**
- `video` - Scrape single video
- `channel` - Scrape entire channel
- `search` - Search stored captions
- `export` - Export video captions to file
- `extract` - Extract video directly to file (no database)
- `stats` - Show database statistics

### 4. Simple Extractor (`extract_video.py`)

Quick script to extract captions from a single video to a text file without database storage.

## Usage Examples

### Single Video Extraction

```bash
# Extract video captions directly to text file
python extract_video.py "https://youtube.com/watch?v=VIDEO_ID" "output.txt"

# Alternative: Extract and store in database
python youtube_cli.py video "https://youtube.com/watch?v=VIDEO_ID"
```

### Channel Scraping

```bash
# Scrape all videos from a channel
python youtube_cli.py channel "https://youtube.com/@channelname"

# Limit to first 50 videos
python youtube_cli.py channel "https://youtube.com/@channelname" --max-videos 50

# Different channel URL formats supported:
python youtube_cli.py channel "https://youtube.com/c/channelname"
python youtube_cli.py channel "https://youtube.com/user/username"
python youtube_cli.py channel "https://youtube.com/channel/UC..."
```

### Searching Captions

```bash
# Search for content across all stored videos
python youtube_cli.py search "medieval literature"
python youtube_cli.py search "Oxford" --limit 10

# Search results include:
# - Video title and uploader
# - Timestamp where term appears
# - Context around the match
# - Direct YouTube URL with timestamp
```

### Database Management

```bash
# Show database statistics
python youtube_cli.py stats

# List stored videos
python youtube_cli.py list

# Export specific video captions
python youtube_cli.py export VIDEO_ID output.txt
```

## Technical Details

### VTT Caption Parsing

The system downloads captions in WebVTT format and parses them into structured data:

```python
{
    'start_time': '00:02:30.000',
    'end_time': '00:02:34.000', 
    'text': 'Lewis discusses medieval literature'
}
```

### Database Schema

**Videos Table:**
```sql
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    uploader TEXT,
    upload_date TEXT,
    duration INTEGER,
    view_count INTEGER,
    description TEXT,
    thumbnail TEXT,
    channel_id TEXT,
    channel_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    caption_count INTEGER DEFAULT 0
);
```

**Captions Table:**
```sql
CREATE TABLE captions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    text TEXT NOT NULL,
    sequence_number INTEGER,
    FOREIGN KEY (video_id) REFERENCES videos (video_id)
);
```

### Full-Text Search

Uses SQLite FTS5 for fast text searching across all captions:

```sql
CREATE VIRTUAL TABLE captions_fts USING fts5(
    video_id,
    text,
    content='captions',
    content_rowid='id'
);
```

## Error Handling

The system handles common issues:

- **No captions available**: Gracefully skips videos without captions
- **Private/deleted videos**: Logs errors and continues with other videos
- **Rate limiting**: yt-dlp handles YouTube rate limits automatically
- **Network errors**: Retries and error logging
- **Duplicate videos**: Checks database before scraping

## Output Formats

### Text File Output

```
Title: C.S. Lewis on Medieval Literature
Uploader: Lewis Studies Channel
Upload Date: 20231201
Duration: 1800 seconds
Video ID: abc123xyz
URL: https://youtube.com/watch?v=abc123xyz
============================================================

Welcome to today's discussion about medieval literature.
Lewis had fascinating insights about courtly love.
The influence of medieval thought on modern Christianity...
```

### Search Results

```
1. Medieval Literature and Modern Faith (Lewis Studies)
   Video ID: abc123
   Time: 00:05:30 - 00:05:34
   Text: Lewis argues that medieval literature provides crucial insights...
   URL: https://youtube.com/watch?v=abc123&t=5m30s

2. Oxford Lectures on Allegory (Academic Channel)
   Video ID: def456
   Time: 00:12:15 - 00:12:19  
   Text: The medieval allegorical tradition that Lewis studied...
   URL: https://youtube.com/watch?v=def456&t=12m15s
```

## Performance Considerations

- **Channel scraping**: Large channels may take hours to complete
- **Database size**: Full-text search creates additional storage overhead
- **Rate limits**: yt-dlp respects YouTube's rate limiting
- **Memory usage**: Processes one video at a time to manage memory

## Advanced Features

### Batch Processing

```python
# Process multiple channels
channels = [
    "https://youtube.com/@lewis-studies",
    "https://youtube.com/@medieval-lit",
    "https://youtube.com/@oxford-lectures"
]

for channel in channels:
    scraper.scrape_channel(channel, max_videos=100)
```

### Custom Search Queries

```python
# Search with context
results = database.search_captions("Narnia", limit=50)

# Filter by channel
channel_videos = database.get_channel_videos("UC123456")

# Export all captions from channel
for video in channel_videos:
    database.export_video_captions(video['video_id'], f"{video['title']}.txt")
```

### Content Analysis

```python
# Get all captions text
captions = database.get_video_captions(video_id)
full_text = ' '.join([c['text'] for c in captions])

# Word frequency analysis
from collections import Counter
words = full_text.lower().split()
common_words = Counter(words).most_common(50)
```

## Troubleshooting

### Common Issues

**"yt-dlp not found"**
```bash
pip install yt-dlp
# or
pip install --upgrade yt-dlp
```

**"No captions found"**
- Video may not have captions
- Try different language: `--sub-lang es` for Spanish
- Check if auto-captions are available

**"Database locked"**
- Another process may be using the database
- Wait for other operations to complete
- Check file permissions

**"Rate limited"**
- yt-dlp handles this automatically
- Wait and retry
- Consider smaller batch sizes

### Performance Tips

1. **Use max-videos limit** for testing: `--max-videos 10`
2. **Run during off-peak hours** for large channels
3. **Monitor disk space** - captions can accumulate quickly
4. **Regular database maintenance** - vacuum and optimize

## Legal and Ethical Considerations

- Respect YouTube's Terms of Service
- Only scrape public content
- Don't redistribute copyrighted content
- Use for research and personal purposes
- Be mindful of creators' rights
- Consider fair use guidelines

## Integration with Other Systems

The scraped captions can be used for:

- **Content analysis**: Research themes and topics
- **Thumbnail generation**: Create titles from scraped content  
- **Educational research**: Study patterns in educational content
- **Accessibility**: Create searchable transcripts
- **Content recommendation**: Find related videos by topic

This system provides a complete foundation for YouTube caption scraping and analysis, suitable for research, education, and content creation workflows.