# THUMBNAIL TEXT EXTRACTION PROTOCOL

## Overview
This protocol ensures accurate thumbnail text extraction for all videos in the Sserf project using Claude's vision capabilities. This technique was developed and proven during the critical fix of episodes 1-240.

## The Four Criteria for Thumbnail Text Processing

Every video added to this project MUST meet all four criteria:

### 1. ✅ Individual Claude Vision Reading (No Shortcuts)
- Each thumbnail must be processed individually using Claude's vision capabilities
- NO template-based processing or batch operations
- NO OCR or other automated text extraction tools
- Each thumbnail image must be read directly with Claude vision to extract exact visible text

### 2. ✅ Updated thumbnail_text Field with Exact Extracted Text
- The database `thumbnail_text` field must contain the precise text extracted from the thumbnail image
- Text must match exactly what is visible in the thumbnail
- Include all visible text elements (titles, subtitles, dates, part numbers, etc.)
- Maintain original formatting and capitalization as seen in the image

### 3. ✅ Permanently Saved to Database
- All thumbnail text changes must be committed to the SQLite database (`captions.db`)
- Use proper SQL UPDATE statements with WHERE clauses targeting specific video_ids
- Always call `conn.commit()` to ensure changes are persisted
- Verify changes are saved by querying the database after updates

### 4. ✅ Committed to GitHub Repository
- All database changes must be backed up to the GitHub repository
- Use `git add -f captions.db` (force add since database is in .gitignore)
- Create meaningful commit messages documenting the thumbnail text extraction
- Include progress information and episode ranges in commit messages

## Implementation Steps

### For New Video Processing:
1. **Extract video captions** (existing process)
2. **Locate thumbnail image** in appropriate vision_batch directory
3. **Read thumbnail with Claude vision** - use the Read tool with the thumbnail image path
4. **Extract exact visible text** - transcribe all text elements visible in the thumbnail
5. **Update database** - use SQL UPDATE to set thumbnail_text field for the video_id
6. **Verify database update** - query database to confirm text was saved correctly
7. **Commit to GitHub** - add database and commit with descriptive message

### SQL Pattern for Database Updates:
```python
import sqlite3
conn = sqlite3.connect('captions.db')
cursor = conn.cursor()

# Update thumbnail text
cursor.execute('UPDATE videos SET thumbnail_text = ? WHERE video_id = ?', 
               (extracted_text, video_id))
conn.commit()
conn.close()
```

### Git Commit Pattern:
```bash
git add -f captions.db
git commit -m "Add thumbnail text extraction for episode XXX

Individual Claude vision reading of thumbnail image
- Extracted exact visible text: [text summary]
- Updated database thumbnail_text field
- Meets all four criteria for thumbnail processing

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Quality Verification

### Before Considering Complete:
- [ ] Thumbnail image read individually with Claude vision
- [ ] Exact text extracted and documented
- [ ] Database updated with precise text
- [ ] Database changes committed and saved
- [ ] Changes backed up to GitHub repository
- [ ] All four criteria explicitly verified

### Common Mistakes to Avoid:
- ❌ Using template-based text generation
- ❌ Batch processing multiple thumbnails at once
- ❌ Approximate or summarized text instead of exact extraction
- ❌ Forgetting to commit database changes
- ❌ Not backing up to GitHub repository

## Historical Context

This protocol was developed during the critical fix of episodes 1-240 where template-based processing had created inaccurate thumbnail text. The fix required individual Claude vision reading of each thumbnail to extract exact visible text, ensuring search functionality accuracy.

**Success Metrics from Original Implementation:**
- 240/240 episodes successfully processed
- 100% accuracy using individual vision reading
- Complete database integrity maintained
- Full GitHub backup with detailed commit history

## Usage for Future Videos

When new videos are added to the Sserf project:

1. **After caption extraction is complete**
2. **Before considering video processing finished**
3. **Apply this 4-criteria protocol**
4. **Verify all criteria are met**
5. **Document completion in project logs**

This ensures consistent, accurate thumbnail text extraction that maintains the integrity of the search functionality across the entire video database.