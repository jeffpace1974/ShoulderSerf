#!/usr/bin/env python3
"""
Test OCR on a specific thumbnail and save debug images.
"""

import requests
import subprocess
import os
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

def test_specific_thumbnail():
    """Test OCR on the Dymer thumbnail from your screenshot."""
    
    # Let's get the video ID for ep181 (Dymer)
    import sqlite3
    conn = sqlite3.connect('captions.db')
    cursor = conn.execute('''
        SELECT video_id, title, thumbnail 
        FROM videos 
        WHERE title LIKE '%ep181%' OR title LIKE '%Dymer%'
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    if not result:
        print("❌ Could not find Dymer video")
        return
    
    video_id, title, thumbnail_url = result
    print(f"🔍 Testing OCR on: {title}")
    print(f"Video ID: {video_id}")
    print(f"Thumbnail: {thumbnail_url}")
    
    # Download image
    response = requests.get(thumbnail_url, timeout=15)
    if response.status_code != 200:
        print(f"❌ Download failed: {response.status_code}")
        return
    
    print(f"✅ Downloaded: {len(response.content)} bytes")
    
    # Process and save debug images
    image = Image.open(BytesIO(response.content))
    print(f"📐 Original size: {image.size}")
    
    # Save original
    image.save('/home/jeffpace/projects/Sserf/debug_original.png')
    print("💾 Saved: debug_original.png")
    
    # Convert to RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Enhanced version 1: High contrast
    enhanced1 = image.copy()
    enhancer = ImageEnhance.Contrast(enhanced1)
    enhanced1 = enhancer.enhance(3.0)
    enhancer = ImageEnhance.Sharpness(enhanced1)
    enhanced1 = enhancer.enhance(2.0)
    enhanced1.save('/home/jeffpace/projects/Sserf/debug_enhanced1.png')
    print("💾 Saved: debug_enhanced1.png")
    
    # Enhanced version 2: Grayscale high contrast
    enhanced2 = image.convert('L')  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(enhanced2)
    enhanced2 = enhancer.enhance(4.0)
    enhanced2.save('/home/jeffpace/projects/Sserf/debug_enhanced2.png')
    print("💾 Saved: debug_enhanced2.png")
    
    # Enhanced version 3: Threshold (black and white)
    enhanced3 = image.convert('L')
    threshold = 128
    enhanced3 = enhanced3.point(lambda x: 255 if x > threshold else 0)
    enhanced3.save('/home/jeffpace/projects/Sserf/debug_enhanced3.png')
    print("💾 Saved: debug_enhanced3.png")
    
    # Test Tesseract on all versions
    tesseract_exe = "/home/jeffpace/projects/Sserf/tesseract.exe"
    tessdata_dir = "/home/jeffpace/projects/Sserf/tessdata"
    
    env = os.environ.copy()
    env['TESSDATA_PREFIX'] = tessdata_dir
    
    test_files = [
        ('original', '/home/jeffpace/projects/Sserf/debug_original.png'),
        ('enhanced1', '/home/jeffpace/projects/Sserf/debug_enhanced1.png'),
        ('enhanced2', '/home/jeffpace/projects/Sserf/debug_enhanced2.png'),
        ('enhanced3', '/home/jeffpace/projects/Sserf/debug_enhanced3.png'),
    ]
    
    for name, file_path in test_files:
        print(f"\n🔍 Testing {name}...")
        
        # Try different PSM modes
        for psm in [3, 6, 7, 8, 11, 12]:
            try:
                cmd = [tesseract_exe, file_path, 'stdout', '-l', 'eng', '--psm', str(psm)]
                result = subprocess.run(cmd, capture_output=True, text=False, env=env, timeout=15)
                
                if result.returncode == 0 and result.stdout:
                    try:
                        text_output = result.stdout.decode('utf-8', errors='ignore').strip()
                        if text_output:
                            print(f"   PSM {psm}: '{text_output}'")
                        else:
                            print(f"   PSM {psm}: (empty)")
                    except:
                        print(f"   PSM {psm}: (decode error)")
                else:
                    print(f"   PSM {psm}: (no output)")
                    
            except Exception as e:
                print(f"   PSM {psm}: Error - {e}")
    
    print(f"\n📋 Debug Summary:")
    print(f"Check these files to see the image processing:")
    print(f"- debug_original.png (original thumbnail)")
    print(f"- debug_enhanced1.png (high contrast/sharpness)")
    print(f"- debug_enhanced2.png (grayscale high contrast)")
    print(f"- debug_enhanced3.png (black and white threshold)")
    
    conn.close()

if __name__ == "__main__":
    test_specific_thumbnail()