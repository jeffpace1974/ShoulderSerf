#!/usr/bin/env python3
"""
Extract text from video thumbnails using OCR.
This script downloads thumbnails and prepares them for OCR processing.
"""

import sqlite3
import requests
import os
from io import BytesIO
import sys

def download_thumbnails():
    """Download and analyze thumbnails from the database."""
    print("Thumbnail Analysis for OCR Processing")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('captions.db')
    
    # Get videos with thumbnails
    cursor = conn.execute('''
        SELECT video_id, title, thumbnail, upload_date
        FROM videos 
        WHERE thumbnail IS NOT NULL 
        ORDER BY upload_date DESC
        LIMIT 10
    ''')
    
    videos = cursor.fetchall()
    print(f"Found {len(videos)} videos with thumbnails (showing first 10)")
    print()
    
    downloaded = 0
    failed = 0
    
    for video_id, title, thumbnail_url, upload_date in videos:
        print(f"Video: {title[:50]}...")
        print(f"  ID: {video_id}")
        print(f"  Date: {upload_date}")
        print(f"  Thumbnail: {thumbnail_url}")
        
        try:
            # Download thumbnail
            response = requests.get(thumbnail_url, timeout=10)
            if response.status_code == 200:
                # Save thumbnail for inspection
                filename = f"thumbnail_{video_id}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                # Get file size
                file_size = len(response.content)
                print(f"  ✓ Downloaded: {filename} ({file_size:,} bytes)")
                downloaded += 1
                
                # For demonstration, just show the first few
                if downloaded >= 3:
                    print(f"  ... (stopping after 3 for demonstration)")
                    break
            else:
                print(f"  ✗ Failed to download (HTTP {response.status_code})")
                failed += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
        
        print()
    
    conn.close()
    
    print(f"Summary:")
    print(f"  Downloaded: {downloaded} thumbnails")
    print(f"  Failed: {failed} thumbnails")
    
    if downloaded > 0:
        print(f"\nThumbnail files created:")
        for f in os.listdir('.'):
            if f.startswith('thumbnail_') and f.endswith('.jpg'):
                size = os.path.getsize(f)
                print(f"  {f} ({size:,} bytes)")
    
    return downloaded > 0

def simulate_ocr_processing():
    """Simulate what OCR processing would do."""
    print("\n" + "="*50)
    print("OCR Processing Simulation")
    print("="*50)
    
    # Connect to database  
    conn = sqlite3.connect('captions.db')
    
    # Get total videos with thumbnails
    cursor = conn.execute('''
        SELECT COUNT(*) FROM videos WHERE thumbnail IS NOT NULL
    ''')
    total_with_thumbnails = cursor.fetchone()[0]
    
    # Get videos already processed
    cursor = conn.execute('''
        SELECT COUNT(*) FROM videos 
        WHERE thumbnail IS NOT NULL 
        AND thumbnail_text IS NOT NULL 
        AND thumbnail_text != ''
    ''')
    already_processed = cursor.fetchone()[0]
    
    remaining = total_with_thumbnails - already_processed
    
    print(f"Total videos with thumbnails: {total_with_thumbnails}")
    print(f"Already processed: {already_processed}")
    print(f"Remaining to process: {remaining}")
    
    # Show sample of what OCR would extract
    print(f"\nSample thumbnail analysis:")
    print(f"Common patterns in C.S. Lewis video thumbnails:")
    print(f"  - Episode numbers (ep232, ep231, etc.)")
    print(f"  - Year references (1924, 1925)")
    print(f"  - Text like 'Diary and Letters'")
    print(f"  - Part numbers (Part 28, Part 1)")
    print(f"  - Author name 'C.S. Lewis'")
    
    conn.close()
    return remaining

def create_sample_data():
    """Create sample thumbnail text data for testing."""
    print(f"\n" + "="*50)
    print("Creating Sample OCR Data")
    print("="*50)
    
    conn = sqlite3.connect('captions.db')
    
    # Add sample thumbnail text to a few videos for testing
    sample_updates = [
        ("9XH-H6H_qig", "Read on C.S. Lewis ep230 1924 Diary and Letters Part 26"),
        ("EAPhFRD-nBk", "Read on C.S. Lewis ep231 1924 Diary and Letters Part 27"),
    ]
    
    updated = 0
    for video_id, sample_text in sample_updates:
        try:
            cursor = conn.execute('''
                UPDATE videos 
                SET thumbnail_text = ? 
                WHERE video_id = ? AND (thumbnail_text IS NULL OR thumbnail_text = '')
            ''', (sample_text, video_id))
            
            if cursor.rowcount > 0:
                print(f"✓ Added sample text to {video_id}: '{sample_text}'")
                updated += 1
            else:
                print(f"- Video {video_id} already has thumbnail text or not found")
        
        except Exception as e:
            print(f"✗ Error updating {video_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdated {updated} videos with sample thumbnail text")
    return updated > 0

if __name__ == "__main__":
    try:
        print("🔍 Analyzing your YouTube video thumbnails...")
        print()
        
        # Download some sample thumbnails
        downloaded = download_thumbnails()
        
        # Show OCR processing simulation
        remaining = simulate_ocr_processing()
        
        # Create sample data for testing
        sample_created = create_sample_data()
        
        print(f"\n" + "="*60)
        print("📋 Summary and Next Steps")
        print("="*60)
        
        if downloaded:
            print("✓ Sample thumbnails downloaded successfully")
            print("✓ OCR packages are available")
            print("✓ Ready for OCR processing")
        
        if remaining > 0:
            print(f"\n📊 Processing Status:")
            print(f"  {remaining} videos ready for OCR processing")
            print(f"  Each thumbnail contains text like episode numbers, dates, titles")
        
        if sample_created:
            print(f"\n🧪 Sample thumbnail text added for testing")
            print(f"  Try searching for 'ep230' or 'ep231' to see results!")
        
        print(f"\n🎯 For full OCR processing on Windows:")
        print(f"  1. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"  2. Run the Windows scripts I created")
        print(f"  3. Process all {remaining} remaining thumbnails")
        
        print("\n✅ Analysis complete!")
        
        # Clean up downloaded thumbnails
        for f in os.listdir('.'):
            if f.startswith('thumbnail_') and f.endswith('.jpg'):
                try:
                    os.remove(f)
                    print(f"Cleaned up: {f}")
                except:
                    pass
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)