# Database Usage Instructions

## Complete Captions Database Included

The repository now includes the complete, up-to-date captions database as `captions_backup.db.gz`.

### Database Contents
- **244 videos** from Shoulder Serf YouTube channel
- **507,244 searchable caption segments** 
- **Enhanced search capabilities** with semantic expansion
- **Thumbnail text extraction** for improved search accuracy
- **Last updated**: 2025-07-03 with Episode 234

### How to Use the Database

**1. Extract the database:**
```bash
gunzip captions_backup.db.gz
```

**2. Verify the database:**
```bash
python3 youtube_cli.py --db captions_backup.db stats
```

**3. Start the enhanced search interface:**
```bash
python3 simple_captions_search.py
```
Then visit: http://localhost:5009

### Database Details
- **Original size**: 131.0 MB
- **Compressed size**: ~38 MB  
- **Format**: SQLite with FTS5 full-text search
- **Content**: Complete Shoulder Serf channel as of 2025-07-03

### Updating the Database
To update with new videos from the channel:
```bash
python3 youtube_cli.py --db captions_backup.db channel "https://www.youtube.com/channel/UChptV-kf8lnncGh7DA2m8Pw"
```

The database is automatically compressed and included in the repository to ensure you always have access to the complete, searchable caption content with enhanced search capabilities.