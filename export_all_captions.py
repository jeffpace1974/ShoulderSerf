#!/usr/bin/env python3
"""Export all captions from the database to a single text file."""

import sqlite3
import os

def export_all_captions():
    """Export all captions to a comprehensive text file."""
    
    print("Starting export of all captions...")
    
    # Connect to database
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Get all captions with video metadata
    cursor.execute('''
        SELECT 
            v.video_id,
            v.title,
            v.upload_date,
            c.start_time,
            c.end_time,
            c.text,
            c.sequence_number
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        ORDER BY v.upload_date, v.title, c.sequence_number
    ''')
    
    with open('complete_captions_export.txt', 'w', encoding='utf-8') as f:
        f.write('COMPLETE CAPTION EXPORT - Shoulder Serf YouTube Channel\n')
        f.write('=' * 80 + '\n\n')
        
        current_video = None
        row_count = 0
        
        for row in cursor.fetchall():
            video_id, title, upload_date, start_time, end_time, text, seq_num = row
            
            # New video header
            if current_video != video_id:
                if current_video is not None:
                    f.write('\n' + '='*80 + '\n\n')
                
                f.write(f'VIDEO: {title}\n')
                f.write(f'ID: {video_id}\n')
                f.write(f'Upload Date: {upload_date}\n')
                f.write(f'URL: https://www.youtube.com/watch?v={video_id}\n')
                f.write('-' * 80 + '\n\n')
                current_video = video_id
            
            # Caption entry
            f.write(f'[{start_time} - {end_time}] {text}\n')
            row_count += 1
            
            if row_count % 10000 == 0:
                print(f'Exported {row_count:,} caption entries...')
    
    print(f'\nExport complete! {row_count:,} caption entries exported to complete_captions_export.txt')
    
    # Get file size
    file_size = os.path.getsize('complete_captions_export.txt')
    print(f'File size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)')
    
    conn.close()
    return row_count

if __name__ == "__main__":
    export_all_captions()