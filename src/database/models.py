"""Database models for storing YouTube captions and video metadata."""

import sqlite3
import logging
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os


logger = logging.getLogger(__name__)


class CaptionDatabase:
    """SQLite database for storing YouTube captions and video metadata."""
    
    def __init__(self, db_path: str = "captions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS videos (
                        video_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        uploader TEXT,
                        upload_date TEXT,
                        duration INTEGER,
                        view_count INTEGER,
                        description TEXT,
                        thumbnail TEXT,
                        thumbnail_text TEXT,
                        channel_id TEXT,
                        channel_url TEXT,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        caption_count INTEGER DEFAULT 0
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS captions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        text TEXT NOT NULL,
                        sequence_number INTEGER,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id)
                    )
                ''')
                
                # Tags table for video tags
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS video_tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT NOT NULL,
                        tag TEXT NOT NULL,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id),
                        UNIQUE(video_id, tag)
                    )
                ''')
                
                # Playlists table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS playlists (
                        playlist_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        channel_id TEXT,
                        video_count INTEGER DEFAULT 0,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Video-playlist relationship table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS video_playlists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT NOT NULL,
                        playlist_id TEXT NOT NULL,
                        position_in_playlist INTEGER,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id),
                        FOREIGN KEY (playlist_id) REFERENCES playlists (playlist_id),
                        UNIQUE(video_id, playlist_id)
                    )
                ''')
                
                # Create indexes for faster searching
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_captions_video_id 
                    ON captions (video_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_captions_text 
                    ON captions (text)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_videos_channel 
                    ON videos (channel_id)
                ''')
                
                # Indexes for new tables
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_video_tags_video_id 
                    ON video_tags (video_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_video_tags_tag 
                    ON video_tags (tag)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_video_playlists_video_id 
                    ON video_playlists (video_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_video_playlists_playlist_id 
                    ON video_playlists (playlist_id)
                ''')
                
                # Full-text search table for captions
                conn.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS captions_fts USING fts5(
                        video_id,
                        text,
                        content='captions',
                        content_rowid='id'
                    )
                ''')
                
                # Enhanced FTS table for comprehensive search including thumbnails, tags, playlists
                conn.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS enhanced_search_fts USING fts5(
                        video_id,
                        video_title,
                        video_description,
                        thumbnail_text,
                        tags,
                        playlists,
                        caption_text
                    )
                ''')
                
                # Triggers to keep FTS table synchronized
                conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS captions_ai AFTER INSERT ON captions BEGIN
                        INSERT INTO captions_fts(rowid, video_id, text) VALUES (new.id, new.video_id, new.text);
                    END
                ''')
                
                conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS captions_ad AFTER DELETE ON captions BEGIN
                        INSERT INTO captions_fts(captions_fts, rowid, video_id, text) VALUES('delete', old.id, old.video_id, old.text);
                    END
                ''')
                
                conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS captions_au AFTER UPDATE ON captions BEGIN
                        INSERT INTO captions_fts(captions_fts, rowid, video_id, text) VALUES('delete', old.id, old.video_id, old.text);
                        INSERT INTO captions_fts(rowid, video_id, text) VALUES (new.id, new.video_id, new.text);
                    END
                ''')
                
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def video_exists(self, video_id: str) -> bool:
        """Check if video already exists in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT video_id FROM videos WHERE video_id = ?",
                    (video_id,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking video existence: {e}")
            return False
    
    def store_video_data(self, video_info: Dict, captions: List[Dict]) -> bool:
        """Store video metadata and captions in database."""
        video_id = video_info.get('video_id')
        
        if not video_id:
            logger.error("No video_id in video_info")
            return False
        
        if self.video_exists(video_id):
            logger.info(f"Video {video_id} already exists in database")
            return True
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert video metadata
                conn.execute('''
                    INSERT INTO videos (
                        video_id, title, uploader, upload_date, duration,
                        view_count, description, thumbnail, thumbnail_text, 
                        channel_id, channel_url, caption_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_id,
                    video_info.get('title'),
                    video_info.get('uploader'),
                    video_info.get('upload_date'),
                    video_info.get('duration'),
                    video_info.get('view_count'),
                    video_info.get('description'),
                    video_info.get('thumbnail'),
                    video_info.get('thumbnail_text'),
                    video_info.get('channel_id'),
                    video_info.get('channel_url'),
                    len(captions)
                ))
                
                # Insert captions
                for i, caption in enumerate(captions):
                    conn.execute('''
                        INSERT INTO captions (
                            video_id, start_time, end_time, text, sequence_number
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        video_id,
                        caption['start_time'],
                        caption['end_time'],
                        caption['text'],
                        i
                    ))
                
                conn.commit()
                logger.info(f"Stored video {video_id} with {len(captions)} captions")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error storing video data: {e}")
            return False
    
    def get_video_captions(self, video_id: str) -> List[Dict]:
        """Get all captions for a specific video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT start_time, end_time, text, sequence_number
                    FROM captions 
                    WHERE video_id = ?
                    ORDER BY sequence_number
                ''', (video_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting video captions: {e}")
            return []
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get video metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM videos WHERE video_id = ?",
                    (video_id,)
                )
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except sqlite3.Error as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def search_captions(self, query: str, limit: int = 50) -> List[Dict]:
        """Search captions using full-text search with synonym support."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get all synonym variants for the query
                query_variants = self._get_search_synonyms(query)
                logger.info(f"Caption search for variants: {query_variants}")
                
                all_results = []
                seen_results = set()  # To avoid duplicates
                
                # Search for each variant
                for variant in query_variants:
                    try:
                        # Use FTS for better search performance
                        cursor = conn.execute('''
                            SELECT 
                                c.video_id,
                                c.start_time,
                                c.end_time,
                                c.text,
                                v.title,
                                v.uploader,
                                v.upload_date
                            FROM captions_fts fts
                            JOIN captions c ON fts.rowid = c.id
                            JOIN videos v ON c.video_id = v.video_id
                            WHERE captions_fts MATCH ?
                            ORDER BY bm25(captions_fts)
                            LIMIT ?
                        ''', (variant, limit))
                        
                        for row in cursor.fetchall():
                            result = dict(row)
                            # Create unique key to avoid duplicates
                            result_key = f"{result['video_id']}_{result['start_time']}_{result['end_time']}"
                            
                            if result_key not in seen_results:
                                seen_results.add(result_key)
                                all_results.append(result)
                    
                    except sqlite3.Error:
                        # Fallback to simple search for this variant
                        fallback_results = self._simple_search(variant, limit)
                        for result in fallback_results:
                            result_key = f"{result['video_id']}_{result['start_time']}_{result['end_time']}"
                            if result_key not in seen_results:
                                seen_results.add(result_key)
                                all_results.append(result)
                
                # Sort by upload date and limit results
                all_results.sort(key=lambda x: (x['upload_date'] or ''), reverse=True)
                final_results = all_results[:limit]
                
                logger.info(f"Caption search found {len(final_results)} results for '{query}' (searched variants: {query_variants})")
                return final_results
                
        except sqlite3.Error as e:
            logger.error(f"Error searching captions: {e}")
            # Fallback to simple LIKE search
            return self._simple_search(query, limit)
    
    def _simple_search(self, query: str, limit: int = 50) -> List[Dict]:
        """Fallback simple text search."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT 
                        c.video_id,
                        c.start_time,
                        c.end_time,
                        c.text,
                        v.title,
                        v.uploader,
                        v.upload_date
                    FROM captions c
                    JOIN videos v ON c.video_id = v.video_id
                    WHERE c.text LIKE ?
                    ORDER BY c.video_id, c.sequence_number
                    LIMIT ?
                ''', (f'%{query}%', limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error in simple search: {e}")
            return []
    
    def _get_search_synonyms(self, query: str) -> List[str]:
        """
        Get search synonyms for common transcription errors.
        
        Args:
            query: Original search query
            
        Returns:
            List of query variants including the original
        """
        # Define synonym mappings for common transcription errors
        synonyms = {
            'maureen': ['maureen', 'moren', 'meen', 'maurine', 'moreen'],
            'moren': ['maureen', 'moren', 'meen', 'maurine', 'moreen'],
            'meen': ['maureen', 'moren', 'meen', 'maurine', 'moreen'],
            # Add more mappings as needed
            'tolkien': ['tolkien', 'tolkin', 'tolkein'],
            'narnia': ['narnia', 'narnea', 'narnya'],
        }
        
        # Convert query to lowercase for matching
        query_lower = query.lower().strip()
        
        # Check if query matches any synonym groups
        if query_lower in synonyms:
            return synonyms[query_lower]
        
        # If no synonyms found, return original query
        return [query]

    def search_concept(self, analysis: Dict, limit: int = 100) -> List[Dict]:
        """
        Semantic concept search using AI-generated analysis.
        Uses flexible word-based matching instead of exact phrases.
        """
        logger.info(f"Performing concept search with analysis: {analysis}")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            all_results = []
            seen_results = set()
            
            # Extract all search terms from analysis
            search_terms = analysis.get('search_terms', [])
            scenario_terms = analysis.get('scenario_terms', [])
            psychological_terms = analysis.get('psychological_terms', [])
            contextual_phrases = analysis.get('contextual_phrases', [])
            
            # Combine all terms for flexible searching
            all_terms = search_terms + scenario_terms + psychological_terms
            
            # Remove duplicates and Lewis name (too broad)
            all_terms = [term.lower() for term in all_terms if term.lower() not in ['lewis', 'jack', 'c.s. lewis']]
            all_terms = list(set(all_terms))
            
            logger.info(f"Concept search using terms: {all_terms[:10]}")
            
            # Search for content containing any combination of terms
            for i, term in enumerate(all_terms[:15]):  # Limit to prevent too many queries
                escaped_term = term.replace('%', '\\%').replace('_', '\\_')
                
                cursor = conn.execute('''
                    SELECT DISTINCT
                        v.video_id,
                        v.title,
                        v.uploader,
                        v.upload_date,
                        v.thumbnail,
                        v.thumbnail_text,
                        c.start_time,
                        c.end_time,
                        c.text,
                        GROUP_CONCAT(DISTINCT vt.tag) as tags,
                        GROUP_CONCAT(DISTINCT p.title) as playlists,
                        'caption' as match_type
                    FROM videos v
                    LEFT JOIN captions c ON v.video_id = c.video_id
                    LEFT JOIN video_tags vt ON v.video_id = vt.video_id
                    LEFT JOIN video_playlists vp ON v.video_id = vp.video_id
                    LEFT JOIN playlists p ON vp.playlist_id = p.playlist_id
                    WHERE 
                        LOWER(c.text) LIKE LOWER(?) OR
                        LOWER(v.title) LIKE LOWER(?) OR
                        LOWER(COALESCE(v.thumbnail_text, '')) LIKE LOWER(?)
                    GROUP BY v.video_id, c.id
                    ORDER BY c.start_time
                    LIMIT ?
                ''', (f'%{escaped_term}%', f'%{escaped_term}%', f'%{escaped_term}%', limit))
                
                for row in cursor.fetchall():
                    result_dict = dict(row)
                    result_key = f"{result_dict['video_id']}_{result_dict['text'][:50]}"
                    
                    if result_key not in seen_results:
                        seen_results.add(result_key)
                        
                        # Add concept matching score with weighted priorities
                        text_lower = result_dict['text'].lower()
                        matched_search_terms = [term for term in search_terms if term.lower() in text_lower]
                        matched_scenario_terms = [term for term in scenario_terms if term.lower() in text_lower]
                        matched_psych_terms = [term for term in psychological_terms if term.lower() in text_lower]
                        
                        # Weight search terms higher than scenario/psychological terms
                        concept_score = (len(matched_search_terms) * 10 +  # High priority
                                       len(matched_scenario_terms) * 3 +   # Medium priority  
                                       len(matched_psych_terms) * 1)       # Low priority
                        
                        result_dict['concept_match_terms'] = matched_search_terms + matched_scenario_terms + matched_psych_terms
                        result_dict['concept_score'] = concept_score
                        
                        all_results.append(result_dict)
            
            logger.info(f"Concept search found {len(all_results)} results")
            return all_results[:limit]

    def _search_multi_word_keywords(self, words: List[str], limit: int = 50) -> List[Dict]:
        """
        Search for content containing ALL specified words (Boolean AND logic).
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Create WHERE conditions for each word
            conditions = []
            params = []
            
            for word in words:
                escaped_word = word.lower().replace('%', '\\%').replace('_', '\\_')
                # Each word must appear in the text
                conditions.append('LOWER(c.text) LIKE LOWER(?)')
                params.append(f'%{escaped_word}%')
            
            where_clause = ' AND '.join(conditions)
            
            logger.info(f"Multi-word search: {where_clause} with params: {params}")
            
            cursor = conn.execute(f'''
                SELECT DISTINCT
                    v.video_id,
                    v.title,
                    v.uploader,
                    v.upload_date,
                    v.thumbnail,
                    v.thumbnail_text,
                    c.start_time,
                    c.end_time,
                    c.text,
                    GROUP_CONCAT(DISTINCT vt.tag) as tags,
                    GROUP_CONCAT(DISTINCT p.title) as playlists,
                    'caption' as match_type
                FROM videos v
                LEFT JOIN captions c ON v.video_id = c.video_id
                LEFT JOIN video_tags vt ON v.video_id = vt.video_id
                LEFT JOIN video_playlists vp ON v.video_id = vp.video_id
                LEFT JOIN playlists p ON vp.playlist_id = p.playlist_id
                WHERE {where_clause}
                GROUP BY v.video_id, c.id
                ORDER BY c.start_time
                LIMIT ?
            ''', params + [limit])
            
            results = []
            for row in cursor.fetchall():
                result_dict = dict(row)
                
                # Add keyword match score
                result_dict['keyword_match_count'] = len([word for word in words if word.lower() in result_dict['text'].lower()])
                
                results.append(result_dict)
            
            logger.info(f"Multi-word keyword search found {len(results)} results")
            return results

    def search_enhanced(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Enhanced search including captions, thumbnail text, tags, and playlists.
        Includes automatic handling of common transcription errors and synonyms.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search results with enhanced metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Check if this is a multi-word keyword search
                query_words = query.strip().split()
                is_multi_word = len(query_words) > 1
                
                if is_multi_word:
                    # Multi-word keyword search: find content containing ALL words
                    logger.info(f"Multi-word keyword search for: {query_words}")
                    return self._search_multi_word_keywords(query_words, limit)
                
                # Single word search - use existing logic with synonyms
                query_variants = self._get_search_synonyms(query)
                logger.info(f"Single word search for variants: {query_variants}")
                
                all_results = []
                seen_results = set()  # To avoid duplicates
                
                # Search for each variant and combine results
                for variant in query_variants:
                    # Enhanced search with word boundary matching
                    # Escape special characters for SQL LIKE pattern
                    escaped_query = variant.replace('%', '\\%').replace('_', '\\_')
                    
                    # Single words use word boundary matching
                    word_pattern = f'% {escaped_query} %'
                    start_pattern = f'{escaped_query} %'
                    end_pattern = f'% {escaped_query}'
                    exact_pattern = escaped_query
                    
                    cursor = conn.execute('''
                        SELECT DISTINCT
                            v.video_id,
                            v.title,
                            v.uploader,
                            v.upload_date,
                            v.thumbnail,
                            v.thumbnail_text,
                            c.start_time,
                            c.end_time,
                            c.text,
                            GROUP_CONCAT(DISTINCT vt.tag) as tags,
                            GROUP_CONCAT(DISTINCT p.title) as playlists,
                            'caption' as match_type
                        FROM videos v
                        LEFT JOIN captions c ON v.video_id = c.video_id
                        LEFT JOIN video_tags vt ON v.video_id = vt.video_id
                        LEFT JOIN video_playlists vp ON v.video_id = vp.video_id
                        LEFT JOIN playlists p ON vp.playlist_id = p.playlist_id
                        WHERE 
                            (' ' || LOWER(c.text) || ' ') LIKE LOWER(?) OR
                            (' ' || LOWER(c.text) || ' ') LIKE LOWER(?) OR
                            (' ' || LOWER(c.text) || ' ') LIKE LOWER(?) OR
                            LOWER(c.text) = LOWER(?) OR
                            (' ' || LOWER(v.title) || ' ') LIKE LOWER(?) OR
                            (' ' || LOWER(v.title) || ' ') LIKE LOWER(?) OR
                            (' ' || LOWER(v.title) || ' ') LIKE LOWER(?) OR
                            LOWER(v.title) = LOWER(?) OR
                            (' ' || LOWER(COALESCE(v.description, '')) || ' ') LIKE LOWER(?) OR
                            (' ' || LOWER(COALESCE(v.thumbnail_text, '')) || ' ') LIKE LOWER(?) OR
                            LOWER(COALESCE(vt.tag, '')) = LOWER(?) OR
                            LOWER(COALESCE(p.title, '')) = LOWER(?)
                        GROUP BY v.video_id, c.id
                        ORDER BY 
                            CASE 
                                WHEN LOWER(c.text) = LOWER(?) THEN 1
                                WHEN (' ' || LOWER(c.text) || ' ') LIKE LOWER(?) THEN 2
                                WHEN LOWER(v.title) = LOWER(?) THEN 3
                                WHEN (' ' || LOWER(v.title) || ' ') LIKE LOWER(?) THEN 4
                                WHEN (' ' || LOWER(COALESCE(v.thumbnail_text, '')) || ' ') LIKE LOWER(?) THEN 5
                                WHEN LOWER(COALESCE(vt.tag, '')) = LOWER(?) THEN 6
                                WHEN LOWER(COALESCE(p.title, '')) = LOWER(?) THEN 7
                                ELSE 8
                            END,
                            v.upload_date DESC
                        LIMIT ?
                    ''', (
                        # Search patterns for captions (word boundaries)
                        word_pattern, start_pattern, end_pattern, exact_pattern,
                        # Search patterns for titles (word boundaries)  
                        word_pattern, start_pattern, end_pattern, exact_pattern,
                        # Search patterns for other fields
                        word_pattern, word_pattern, exact_pattern, exact_pattern,
                        # Priority order patterns
                        exact_pattern, word_pattern, exact_pattern, word_pattern,
                        word_pattern, exact_pattern, exact_pattern,
                        limit
                    ))
                    
                    # Process results for this variant
                    for row in cursor.fetchall():
                        result = dict(row)
                        # Create unique key to avoid duplicates
                        result_key = f"{result['video_id']}_{result['start_time']}_{result['end_time']}"
                        
                        if result_key not in seen_results:
                            seen_results.add(result_key)
                            # Parse tags and playlists
                            result['tags'] = result['tags'].split(',') if result['tags'] else []
                            result['playlists'] = result['playlists'].split(',') if result['playlists'] else []
                            all_results.append(result)
                
                # Sort combined results by relevance and date
                all_results.sort(key=lambda x: (x['upload_date'] or ''), reverse=True)
                
                # Limit final results
                final_results = all_results[:limit]
                
                logger.info(f"Enhanced search found {len(final_results)} results for '{query}' (searched variants: {query_variants})")
                return final_results
                
        except sqlite3.Error as e:
            logger.error(f"Error in enhanced search: {e}")
            # Fallback to regular search
            return self.search_captions(query, limit)
    
    def get_channel_videos(self, channel_id: str) -> List[Dict]:
        """Get all videos from a specific channel."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT video_id, title, uploader, upload_date, caption_count
                    FROM videos 
                    WHERE channel_id = ?
                    ORDER BY upload_date DESC
                ''', (channel_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting channel videos: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get video count
                video_count = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
                
                # Get caption count
                caption_count = conn.execute("SELECT COUNT(*) FROM captions").fetchone()[0]
                
                # Get channel count
                channel_count = conn.execute(
                    "SELECT COUNT(DISTINCT channel_id) FROM videos WHERE channel_id IS NOT NULL"
                ).fetchone()[0]
                
                # Get most recent video
                cursor = conn.execute(
                    "SELECT MAX(scraped_at) FROM videos"
                )
                last_scraped = cursor.fetchone()[0]
                
                return {
                    'video_count': video_count,
                    'caption_count': caption_count,
                    'channel_count': channel_count,
                    'last_scraped': last_scraped,
                    'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_video_captions(self, video_id: str, output_path: str) -> bool:
        """Export video captions to text file."""
        try:
            video_info = self.get_video_info(video_id)
            captions = self.get_video_captions(video_id)
            
            if not video_info or not captions:
                logger.error(f"No data found for video {video_id}")
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {video_info['title']}\n")
                f.write(f"Uploader: {video_info['uploader']}\n")
                f.write(f"Upload Date: {video_info['upload_date']}\n")
                f.write(f"Video ID: {video_id}\n")
                f.write("=" * 50 + "\n\n")
                
                for caption in captions:
                    f.write(f"[{caption['start_time']} - {caption['end_time']}]\n")
                    f.write(f"{caption['text']}\n\n")
            
            logger.info(f"Exported captions to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting captions: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """Delete video and its captions from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM captions WHERE video_id = ?", (video_id,))
                conn.execute("DELETE FROM videos WHERE video_id = ?", (video_id,))
                conn.commit()
                
                logger.info(f"Deleted video {video_id} from database")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    def store_video_tags(self, video_id: str, tags: List[str]) -> bool:
        """Store video tags in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Clear existing tags for this video
                conn.execute("DELETE FROM video_tags WHERE video_id = ?", (video_id,))
                
                # Insert new tags
                for tag in tags:
                    conn.execute('''
                        INSERT OR IGNORE INTO video_tags (video_id, tag) 
                        VALUES (?, ?)
                    ''', (video_id, tag))
                
                conn.commit()
                logger.info(f"Stored {len(tags)} tags for video {video_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error storing video tags: {e}")
            return False
    
    def store_playlist(self, playlist_info: Dict) -> bool:
        """Store playlist metadata in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO playlists (
                        playlist_id, title, description, channel_id, video_count
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    playlist_info.get('playlist_id'),
                    playlist_info.get('title'),
                    playlist_info.get('description'),
                    playlist_info.get('channel_id'),
                    playlist_info.get('video_count', 0)
                ))
                
                conn.commit()
                logger.info(f"Stored playlist {playlist_info.get('playlist_id')}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error storing playlist: {e}")
            return False
    
    def store_video_playlist_relationship(self, video_id: str, playlist_id: str, position: int = None) -> bool:
        """Store video-playlist relationship."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR IGNORE INTO video_playlists (
                        video_id, playlist_id, position_in_playlist
                    ) VALUES (?, ?, ?)
                ''', (video_id, playlist_id, position))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error storing video-playlist relationship: {e}")
            return False
    
    def update_thumbnail_text(self, video_id: str, thumbnail_text: str) -> bool:
        """Update thumbnail text for a video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE videos SET thumbnail_text = ? WHERE video_id = ?
                ''', (thumbnail_text, video_id))
                
                conn.commit()
                logger.info(f"Updated thumbnail text for video {video_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error updating thumbnail text: {e}")
            return False
    
    def get_video_tags(self, video_id: str) -> List[str]:
        """Get tags for a specific video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT tag FROM video_tags WHERE video_id = ?
                ''', (video_id,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting video tags: {e}")
            return []
    
    def get_video_playlists(self, video_id: str) -> List[Dict]:
        """Get playlists containing a specific video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT p.playlist_id, p.title, p.description, vp.position_in_playlist
                    FROM playlists p
                    JOIN video_playlists vp ON p.playlist_id = vp.playlist_id
                    WHERE vp.video_id = ?
                    ORDER BY vp.position_in_playlist
                ''', (video_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting video playlists: {e}")
            return []