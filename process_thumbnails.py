#!/usr/bin/env python3
"""
Process all video thumbnails to extract text using OCR
Windows-friendly version with progress tracking.
"""

import sys
import os
import sqlite3
import requests
from PIL import Image
import pytesseract
from io import BytesIO
import time

def setup_ocr():
    """Load OCR configuration."""
    if os.path.exists("ocr_config.py"):
        print("Loading OCR configuration...")
        exec(open("ocr_config.py").read())
        print("✓ OCR configuration loaded")
        return True
    else:
        print("❌ OCR configuration not found!")
        print("Please run: python setup_ocr_python.py")
        return False

def extract_text_from_url(image_url, video_id):
    """Extract text from an image URL using OCR."""
    try:
        # Download image
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None, f"Failed to download image (HTTP {response.status_code})"
        
        # Open image
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(image, 
                                                   config='--psm 6 --oem 3').strip()
        
        # Clean up text
        if extracted_text:
            # Remove extra whitespace and newlines
            extracted_text = ' '.join(extracted_text.split())
            # Only keep if it's meaningful (more than 2 characters)
            if len(extracted_text) > 2:
                return extracted_text, None
        
        return None, "No meaningful text found"
        
    except Exception as e:
        return None, str(e)

def process_all_thumbnails():
    """Process all video thumbnails and extract text."""
    print("=" * 60)
    print("         Processing Video Thumbnails with OCR")
    print("=" * 60)
    print()
    
    # Setup OCR
    if not setup_ocr():
        return False
    
    # Connect to database
    try:
        conn = sqlite3.connect('captions.db')
        
        # Get all videos with thumbnails that don't have text yet
        cursor = conn.execute('''
            SELECT video_id, title, thumbnail 
            FROM videos 
            WHERE thumbnail IS NOT NULL 
            AND (thumbnail_text IS NULL OR thumbnail_text = '')
            ORDER BY upload_date DESC
        ''')
        
        videos_to_process = cursor.fetchall()
        total_videos = len(videos_to_process)
        
        if total_videos == 0:
            print("✓ All videos with thumbnails already have OCR text extracted!")
            conn.close()
            return True
        
        print(f"Found {total_videos} videos with thumbnails to process")
        print()
        
        # Process each video
        successful = 0
        failed = 0
        
        for i, (video_id, title, thumbnail_url) in enumerate(videos_to_process, 1):
            print(f"[{i}/{total_videos}] Processing: {title[:50]}...")
            print(f"   Video ID: {video_id}")
            
            # Extract text from thumbnail
            extracted_text, error = extract_text_from_url(thumbnail_url, video_id)
            
            if extracted_text:
                # Update database with extracted text
                conn.execute('''
                    UPDATE videos 
                    SET thumbnail_text = ? 
                    WHERE video_id = ?
                ''', (extracted_text, video_id))
                
                print(f"   ✓ Text extracted: '{extracted_text[:50]}...'")
                successful += 1
            else:
                print(f"   ⚠️  OCR failed: {error}")
                failed += 1
            
            # Commit every 10 videos to save progress
            if i % 10 == 0:
                conn.commit()
                print(f"\n   Progress saved: {i}/{total_videos} videos processed\n")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        # Final commit
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 Thumbnail Processing Complete!")
        print(f"✓ Successfully processed: {successful} videos")
        print(f"⚠️  Failed to process: {failed} videos")
        print(f"📊 Success rate: {(successful/(successful+failed)*100):.1f}%")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing thumbnails: {e}")
        return False

def show_sample_results():
    """Show sample OCR results."""
    try:
        conn = sqlite3.connect('captions.db')
        cursor = conn.execute('''
            SELECT title, thumbnail_text 
            FROM videos 
            WHERE thumbnail_text IS NOT NULL 
            AND thumbnail_text != ''
            ORDER BY RANDOM()
            LIMIT 5
        ''')
        
        results = cursor.fetchall()
        if results:
            print("\n📋 Sample OCR Results:")
            print("-" * 50)
            for title, text in results:
                print(f"Video: {title[:40]}...")
                print(f"Text:  {text[:60]}...")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Could not show sample results: {e}")

if __name__ == "__main__":
    try:
        success = process_all_thumbnails()
        
        if success:
            show_sample_results()
            print("\n✅ OCR processing completed!")
            print("\nThe search system will now include thumbnail text in results.")
            print("Try searching for text that might appear in video thumbnails!")
        else:
            print("\n❌ OCR processing failed!")
            print("Please run: python setup_ocr_python.py")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\nProcessing cancelled by user.")
        print("Progress has been saved to the database.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        input("Press Enter to exit...")