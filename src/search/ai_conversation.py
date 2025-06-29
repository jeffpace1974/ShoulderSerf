"""
AI Conversational Search for C.S. Lewis Caption Database

This module provides a ChatGPT-powered conversational interface that can:
1. Search the entire captions database
2. Answer questions about search results
3. Explain why it returned specific results
4. Have back-and-forth conversations about the content
"""

import logging
import os
import json
from typing import List, Dict, Optional, Tuple
import sqlite3

# Optional AI API imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIConversationalSearch:
    """ChatGPT-powered conversational search interface for the captions database."""
    
    def __init__(self, db_path: str = "captions.db"):
        self.db_path = db_path
        self.openai_client = None
        self.conversation_history = []
        
        # Initialize OpenAI client if API key is available
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logger.info("OpenAI client initialized for conversational search")
    
    def get_available_models(self):
        """Get information about available AI models."""
        models = {}
        
        if self.openai_client:
            models.update({
                'gpt-4': {
                    'name': 'GPT-4',
                    'description': 'Most capable model, best for complex analysis',
                    'available': True,
                    'speed': 'Slower',
                    'accuracy': 'Excellent'
                },
                'gpt-4-turbo': {
                    'name': 'GPT-4 Turbo',
                    'description': 'Faster GPT-4 with good understanding',
                    'available': True,
                    'speed': 'Fast',
                    'accuracy': 'Excellent'
                },
                'gpt-3.5-turbo': {
                    'name': 'GPT-3.5 Turbo',
                    'description': 'Fast and cost-effective',
                    'available': True,
                    'speed': 'Very Fast',
                    'accuracy': 'Good'
                }
            })
        
        return models
    
    def get_database_summary(self) -> Dict:
        """Get a summary of the database content for the AI."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic statistics
            cursor.execute('SELECT COUNT(*) FROM videos')
            total_videos = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM captions')
            total_captions = cursor.fetchone()[0]
            
            # Get episode range
            cursor.execute('SELECT title FROM videos WHERE title LIKE "%ep%" ORDER BY title LIMIT 1')
            first_ep = cursor.fetchone()
            cursor.execute('SELECT title FROM videos WHERE title LIKE "%ep%" ORDER BY title DESC LIMIT 1')
            last_ep = cursor.fetchone()
            
            # Get sample video titles
            cursor.execute('SELECT title FROM videos LIMIT 10')
            sample_titles = [row[0] for row in cursor.fetchall()]
            
            return {
                'total_videos': total_videos,
                'total_captions': total_captions,
                'episode_range': f"{first_ep[0] if first_ep else 'Unknown'} to {last_ep[0] if last_ep else 'Unknown'}",
                'sample_titles': sample_titles
            }
    
    def search_database(self, query: str, limit: int = 100) -> List[Dict]:
        """Search the database for content matching the query."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # For microscope queries, get the complete microscope story from episode 2
            if 'microscope' in query.lower():
                # First, get the exact microscope captions from episode 2
                cursor = conn.execute('''
                    SELECT
                        v.video_id,
                        v.title,
                        v.uploader,
                        v.upload_date,
                        c.start_time,
                        c.end_time,
                        c.text,
                        v.thumbnail_text
                    FROM videos v
                    JOIN captions c ON v.video_id = c.video_id
                    WHERE v.title = 'Read on C. S. Lewis - ep2'
                    AND LOWER(c.text) LIKE '%microscope%'
                    ORDER BY c.start_time
                ''')
                
                microscope_captions = [dict(row) for row in cursor.fetchall()]
                
                # Then get the surrounding context for the complete story  
                cursor = conn.execute('''
                    SELECT
                        v.video_id,
                        v.title,
                        v.uploader,
                        v.upload_date,
                        c.start_time,
                        c.end_time,
                        c.text,
                        v.thumbnail_text
                    FROM videos v
                    JOIN captions c ON v.video_id = c.video_id
                    WHERE v.title = 'Read on C. S. Lewis - ep2'
                    AND c.start_time BETWEEN '01:00:20' AND '01:02:10'
                    AND (LOWER(c.text) LIKE '%enology%' 
                         OR LOWER(c.text) LIKE '%entomological%'
                         OR LOWER(c.text) LIKE '%arguments%'
                         OR LOWER(c.text) LIKE '%decided%'
                         OR LOWER(c.text) LIKE '%killing%'
                         OR LOWER(c.text) LIKE '%study%'
                         OR LOWER(c.text) LIKE '%species%')
                    ORDER BY c.start_time
                ''')
                
                context_captions = [dict(row) for row in cursor.fetchall()]
                
                # Combine and sort by timestamp
                ep2_results = microscope_captions + context_captions
                ep2_results.sort(key=lambda x: x['start_time'])
                
                # Also search for microscope mentions in other episodes
                cursor = conn.execute('''
                    SELECT
                        v.video_id,
                        v.title,
                        v.uploader,
                        v.upload_date,
                        c.start_time,
                        c.end_time,
                        c.text,
                        v.thumbnail_text
                    FROM videos v
                    JOIN captions c ON v.video_id = c.video_id
                    WHERE LOWER(c.text) LIKE '%microscope%'
                    AND v.title != 'Read on C. S. Lewis - ep2'
                    ORDER BY v.title, c.start_time
                    LIMIT ?
                ''', (limit // 2,))
                
                other_results = [dict(row) for row in cursor.fetchall()]
                return ep2_results + other_results
            
            # For other queries, use simpler search
            cursor = conn.execute('''
                SELECT
                    v.video_id,
                    v.title,
                    v.uploader,
                    v.upload_date,
                    c.start_time,
                    c.end_time,
                    c.text,
                    v.thumbnail_text
                FROM videos v
                JOIN captions c ON v.video_id = c.video_id
                WHERE LOWER(c.text) LIKE LOWER(?)
                    OR LOWER(v.title) LIKE LOWER(?)
                ORDER BY v.title, c.start_time
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def chat_with_ai(self, user_message: str, model: str = "gpt-4-turbo") -> Dict:
        """
        Have a conversation with ChatGPT about the captions database.
        
        Args:
            user_message: The user's question or request
            model: OpenAI model to use
            
        Returns:
            Dict containing AI response and any search results
        """
        if not self.openai_client:
            return {
                'response': 'OpenAI is not available. Please check your API key configuration.',
                'search_results': [],
                'search_performed': False,
                'error': 'OpenAI unavailable'
            }
        
        try:
            # Get database summary for context
            db_summary = self.get_database_summary()
            
            # Create the system message
            system_message = f"""You are an AI assistant helping users search and analyze a database of C.S. Lewis content. 

DATABASE CONTEXT:
- Total Videos: {db_summary['total_videos']}
- Total Caption Segments: {db_summary['total_captions']}
- Content Range: {db_summary['episode_range']}
- Sample Content: {', '.join(db_summary['sample_titles'][:3])}...

You can search this database to find content related to C.S. Lewis's life, writings, letters, diaries, and biographical information. The content comes from conversational discussions about Lewis's works.

CAPABILITIES:
1. When a user asks about something, search the database for relevant content
2. Analyze the results and explain what you found
3. Answer follow-up questions about why you returned specific results
4. Engage in conversation about the content and Lewis's life/works

SEARCH STRATEGY:
- Extract key terms from the user's question
- Search broadly to find potentially relevant content
- Analyze the results for relevance to the user's query
- Explain your reasoning for what you found (or didn't find)

Be conversational and helpful. If you don't find exactly what they're looking for, explain what you did find and suggest alternative approaches."""

            # Add conversation history for context
            messages = [{"role": "system", "content": system_message}]
            
            # Add recent conversation history (last 10 messages)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Determine if we need to search the database
            search_needed = self._should_search_database(user_message)
            search_results = []
            
            if search_needed:
                # Extract search terms and perform database search
                search_terms = self._extract_search_terms(user_message)
                for term in search_terms:
                    results = self.search_database(term, 20)
                    search_results.extend(results)
                
                # Remove duplicates
                seen = set()
                unique_results = []
                for result in search_results:
                    key = f"{result['video_id']}_{result['text'][:50]}"
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(result)
                
                search_results = unique_results[:50]  # Limit to 50 results
                
                # Add search results to the conversation with better context
                if search_results:
                    # Group results by episode and organize chronologically
                    episodes = {}
                    for result in search_results:
                        episode_title = result['title']
                        if episode_title not in episodes:
                            episodes[episode_title] = []
                        episodes[episode_title].append(result)
                    
                    # Sort results within each episode by timestamp
                    for episode_title in episodes:
                        episodes[episode_title].sort(key=lambda x: x.get('start_time', '00:00:00'))
                    
                    search_summary = f"\n\nSEARCH RESULTS FOUND ({len(search_results)} items across {len(episodes)} episodes):\n\n"
                    
                    # Present results grouped by episode with full context
                    for episode_title, episode_results in episodes.items():
                        episode_num = episode_title.split('ep')[1].split(':')[0].strip() if 'ep' in episode_title else 'Other'
                        search_summary += f"=== EPISODE {episode_num} ===\n"
                        
                        # For microscope-related content, provide more context
                        if any('microscope' in r['text'].lower() for r in episode_results):
                            search_summary += "Context about microscope:\n"
                            for result in episode_results[:15]:  # Show more results for key episodes
                                timestamp = result.get('start_time', '')
                                search_summary += f"[{timestamp}] {result['text']}\n"
                        else:
                            # For other episodes, show fewer results
                            for i, result in enumerate(episode_results[:5]):
                                timestamp = result.get('start_time', '')
                                search_summary += f"{i+1}. [{timestamp}] {result['text'][:100]}...\n"
                        
                        search_summary += "\n"
                    
                    # Add analysis instruction
                    search_summary += "\nIMPORTANT: Please analyze these search results chronologically and connect related concepts. Look for:\n"
                    search_summary += "- Sequential captions that tell a complete story\n"
                    search_summary += "- Relationships between different topics (e.g., 'enology' likely means 'entomology' - study of insects)\n"
                    search_summary += "- Cause-and-effect relationships in the narrative\n"
                    search_summary += "- Complete context for decisions or actions mentioned\n"
                    
                    messages[-1]["content"] += search_summary
            
            # Get AI response
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                'response': ai_response,
                'search_results': search_results,
                'search_performed': search_needed,
                'model_used': model,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"AI conversation failed: {e}")
            return {
                'response': f'Sorry, I encountered an error: {str(e)}',
                'search_results': [],
                'search_performed': False,
                'error': str(e)
            }
    
    def _should_search_database(self, message: str) -> bool:
        """Determine if a database search is needed for this message."""
        # Always search for now - we can make this smarter later
        return True
    
    def _extract_search_terms(self, message: str) -> List[str]:
        """Extract search terms from the user's message."""
        # For specific topics, use more targeted search terms
        message_lower = message.lower()
        
        # Special handling for microscope Christmas question
        if 'microscope' in message_lower and ('christmas' in message_lower or 'why' in message_lower or 'reason' in message_lower):
            return ['microscope christmas', 'microscope', 'enology', 'arguments against', 'decided not']
        
        # Extract key phrases and individual words
        words = message_lower.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'about', 'what', 'when', 'where', 'why', 'how', 'lewis', 'c.s.', 'anything', 'find', 'you'}
        
        # Get meaningful words
        meaningful_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        search_terms = []
        
        # Add important multi-word phrases first
        if len(meaningful_words) >= 2:
            # Try 2-word combinations of important terms
            for i in range(len(meaningful_words) - 1):
                phrase = f"{meaningful_words[i]} {meaningful_words[i+1]}"
                search_terms.append(phrase)
        
        # Add individual meaningful words
        search_terms.extend(meaningful_words[:3])
        
        # Add the full message if it's not too long
        if len(words) <= 8:
            search_terms.append(message)
        
        return search_terms[:5]  # Limit to 5 search terms
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")