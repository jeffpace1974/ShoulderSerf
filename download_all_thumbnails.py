#!/usr/bin/env python3
"""
Download all 240 video thumbnails in organized batches for vision processing
"""

import sqlite3
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional

def get_all_videos() -> List[Dict]:
    """Get all videos from database"""
    conn = sqlite3.connect("captions.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT video_id, title, thumbnail 
        FROM videos 
        WHERE thumbnail IS NOT NULL
        ORDER BY video_id
    """)
    
    videos = []
    for row in cursor.fetchall():
        videos.append({
            'video_id': row[0],
            'title': row[1], 
            'thumbnail_url': row[2]
        })
    
    conn.close()
    return videos

def download_thumbnail(video_id: str, thumbnail_url: str, output_dir: Path) -> bool:
    """Download thumbnail image"""
    if not thumbnail_url:
        return False
        
    filename = f"{video_id}.jpg"
    filepath = output_dir / filename
    
    # Skip if already downloaded
    if filepath.exists():
        return True
        
    try:
        response = requests.get(thumbnail_url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except Exception as e:
        print(f"Failed to download {video_id}: {e}")
        return False

def download_batch(videos: List[Dict], batch_num: int):
    """Download a batch of thumbnails"""
    batch_dir = Path(f"vision_batch_{batch_num:02d}")
    batch_dir.mkdir(exist_ok=True)
    
    print(f"Downloading batch {batch_num}: {len(videos)} thumbnails")
    
    # Create batch info file
    info_file = batch_dir / "batch_info.txt"
    with open(info_file, 'w') as f:
        f.write(f"Batch {batch_num}\n")
        f.write(f"Videos: {len(videos)}\n\n")
        for video in videos:
            f.write(f"{video['video_id']}: {video['title']}\n")
    
    downloaded = 0
    for i, video in enumerate(videos):
        if download_thumbnail(video['video_id'], video['thumbnail_url'], batch_dir):
            downloaded += 1
        
        if (i + 1) % 5 == 0:
            print(f"  {i + 1}/{len(videos)} downloaded")
        
        time.sleep(0.1)  # Be respectful to servers
    
    print(f"Batch {batch_num} complete: {downloaded}/{len(videos)} downloaded")
    return downloaded

def main():
    print("Downloading all thumbnails for vision processing...")
    
    videos = get_all_videos()
    total_videos = len(videos)
    batch_size = 20
    
    print(f"Found {total_videos} videos")
    print(f"Will create {(total_videos + batch_size - 1) // batch_size} batches of {batch_size} videos each")
    
    total_downloaded = 0
    batch_num = 1
    
    for i in range(0, total_videos, batch_size):
        batch_videos = videos[i:i + batch_size]
        downloaded = download_batch(batch_videos, batch_num)
        total_downloaded += downloaded
        batch_num += 1
        
        if i + batch_size < total_videos:
            print("Pausing 2 seconds...")
            time.sleep(2)
    
    print(f"\nDownload complete!")
    print(f"Total downloaded: {total_downloaded}/{total_videos}")
    print(f"Thumbnails organized in vision_batch_01, vision_batch_02, etc.")

if __name__ == "__main__":
    main()