#!/usr/bin/env python3
"""
Captions Database Research Chat Interface
Advanced AI-powered interface for deep research into the captions database
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import anthropic
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'captions-research-secret-key')

# Initialize Anthropic client
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
try:
    client = anthropic.Anthropic(api_key=api_key) if api_key else None
    if client and api_key:
        print(f"✅ Anthropic client initialized successfully (key: {api_key[:10]}...)")
    else:
        print("❌ No Anthropic API key found")
        client = None
except Exception as e:
    client = None
    print(f"Anthropic client initialization failed: {e}")

def get_database_context() -> str:
    """Get context about the database structure and content"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Get database stats
    cursor.execute("SELECT COUNT(*) FROM videos")
    video_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM captions")
    segment_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(episode_number), MAX(episode_number) FROM videos WHERE episode_number IS NOT NULL")
    min_ep, max_ep = cursor.fetchone()
    
    conn.close()
    
    return f"""
DATABASE CONTEXT:
- Total videos: {video_count}
- Total caption segments: {segment_count}
- Episode range: {min_ep} to {max_ep}
- Database contains C.S. Lewis content with full-text search capabilities
- Videos table: video_id, title, episode_number, thumbnail, thumbnail_text
- Caption_segments table: video_id, start_time, end_time, text with FTS5 search
"""

def search_database(query: str, episode_filter: Optional[str] = None) -> List[Dict]:
    """Search the captions database with optional episode filtering"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Build search query
    if episode_filter:
        if "before" in episode_filter.lower():
            ep_num = int(''.join(filter(str.isdigit, episode_filter)))
            sql = """
                SELECT v.episode_number, v.title, c.start_time, c.text, v.video_id
                FROM captions cs
                JOIN videos v ON c.video_id = v.video_id
                WHERE v.episode_number < ? AND c.text MATCH ?
                ORDER BY v.episode_number, c.start_time
            """
            cursor.execute(sql, (ep_num, query))
        elif "after" in episode_filter.lower():
            ep_num = int(''.join(filter(str.isdigit, episode_filter)))
            sql = """
                SELECT v.episode_number, v.title, c.start_time, c.text, v.video_id
                FROM captions cs
                JOIN videos v ON c.video_id = v.video_id
                WHERE v.episode_number > ? AND c.text MATCH ?
                ORDER BY v.episode_number, c.start_time
            """
            cursor.execute(sql, (ep_num, query))
        else:
            # Specific episode
            ep_num = int(''.join(filter(str.isdigit, episode_filter)))
            sql = """
                SELECT v.episode_number, v.title, c.start_time, c.text, v.video_id
                FROM captions cs
                JOIN videos v ON c.video_id = v.video_id
                WHERE v.episode_number = ? AND c.text MATCH ?
                ORDER BY c.start_time
            """
            cursor.execute(sql, (ep_num, query))
    else:
        sql = """
            SELECT v.episode_number, v.title, c.start_time, c.text, v.video_id
            FROM captions cs
            JOIN videos v ON c.video_id = v.video_id
            WHERE c.text MATCH ?
            ORDER BY v.episode_number, c.start_time
        """
        cursor.execute(sql, (query,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'episode_number': row[0],
            'title': row[1],
            'start_time': row[2],
            'text': row[3],
            'video_id': row[4],
            'timestamp_url': f"https://youtube.com/watch?v={row[4]}&t={int(row[2])}s"
        })
    
    conn.close()
    return results

def get_episode_context(episode_number: int) -> Dict:
    """Get full context for a specific episode"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM videos WHERE episode_number = ?", (episode_number,))
    video_data = cursor.fetchone()
    
    cursor.execute("""
        SELECT start_time, end_time, text 
        FROM captions 
        WHERE video_id = ? 
        ORDER BY start_time
    """, (video_data[0],))
    
    segments = cursor.fetchall()
    conn.close()
    
    return {
        'video_data': video_data,
        'segments': segments
    }

@app.route('/')
def index():
    """Main research interface"""
    return render_template('captions_research.html')

@app.route('/api/research', methods=['POST'])
def research_query():
    """Handle research queries with AI analysis"""
    try:
        data = request.json
        user_query = data.get('query', '')
        conversation_history = data.get('history', [])
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Check if Anthropic client is available
        if not client:
            return jsonify({
                'error': 'AI functionality not available. Please set ANTHROPIC_API_KEY in your .env file.',
                'setup_instructions': 'Add ANTHROPIC_API_KEY=your_key_here to the .env file and restart the server.'
            }), 503
        
        # Initialize conversation if new
        if 'conversation_id' not in session:
            session['conversation_id'] = str(uuid.uuid4())
        
        # Build context for Claude
        db_context = get_database_context()
        
        # Prepare conversation history for Claude
        messages = []
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": "user" if msg['type'] == 'user' else "assistant",
                "content": msg['content']
            })
        
        # Add current query
        system_prompt = f"""You are an expert researcher with access to a comprehensive C.S. Lewis captions database. Your role is to help users find specific content, analyze patterns, and provide detailed research insights.

{db_context}

CAPABILITIES:
- Perform complex database searches using FTS5 full-text search
- Analyze episode content and cross-reference information
- Find specific quotes, themes, and narrative patterns
- Provide timestamps and YouTube links for found content
- Conduct comparative analysis across episodes

SEARCH TOOLS:
- Use search_database(query, episode_filter) for targeted searches
- Use get_episode_context(episode_number) for full episode analysis
- Combine multiple search strategies for comprehensive research

RESPONSE FORMAT:
- Provide specific episode numbers and timestamps
- Include relevant quotes and context
- Generate YouTube URLs with timestamps
- Offer follow-up research suggestions

The user is asking: {user_query}

Please conduct thorough research and provide detailed findings with specific references."""

        messages.append({
            "role": "user", 
            "content": user_query
        })
        
        # Call Claude with function calling capabilities
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=messages,
            tools=[
                {
                    "name": "search_database",
                    "description": "Search the captions database with FTS5 full-text search",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "FTS5 search query (use quotes for exact phrases, OR/AND for logic)"
                            },
                            "episode_filter": {
                                "type": "string", 
                                "description": "Optional episode filter: 'before 232', 'after 100', 'episode 164', etc."
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_episode_context",
                    "description": "Get full context and all captions for a specific episode",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "episode_number": {
                                "type": "integer",
                                "description": "Episode number to get full context for"
                            }
                        },
                        "required": ["episode_number"]
                    }
                }
            ]
        )
        
        # Process Claude's response and handle tool calls
        assistant_response = ""
        
        for block in response.content:
            if block.type == "text":
                assistant_response += block.text
            elif block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                
                if tool_name == "search_database":
                    search_results = search_database(
                        tool_input.get("query"), 
                        tool_input.get("episode_filter")
                    )
                    
                    # Format results for Claude
                    results_text = "\n\nSEARCH RESULTS:\n"
                    for result in search_results[:20]:  # Limit to 20 results
                        results_text += f"Episode {result['episode_number']}: {result['text'][:200]}... (Timestamp: {result['start_time']}s, URL: {result['timestamp_url']})\n"
                    
                    assistant_response += results_text
                    
                elif tool_name == "get_episode_context":
                    episode_data = get_episode_context(tool_input["episode_number"])
                    
                    context_text = f"\n\nEPISODE {tool_input['episode_number']} CONTEXT:\n"
                    context_text += f"Title: {episode_data['video_data'][1]}\n"
                    context_text += f"Total segments: {len(episode_data['segments'])}\n"
                    
                    assistant_response += context_text
        
        return jsonify({
            'response': assistant_response,
            'conversation_id': session['conversation_id'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/episodes')
def get_episodes():
    """Get list of all episodes"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT episode_number, title, video_id 
        FROM videos 
        WHERE episode_number IS NOT NULL 
        ORDER BY episode_number
    """)
    
    episodes = []
    for row in cursor.fetchall():
        episodes.append({
            'episode_number': row[0],
            'title': row[1],
            'video_id': row[2],
            'url': f"https://youtube.com/watch?v={row[2]}"
        })
    
    conn.close()
    return jsonify(episodes)

if __name__ == '__main__':
    # Check for required environment variables
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Warning: ANTHROPIC_API_KEY not set. Set it in your .env file.")
    
    print("Starting Captions Database Research Chat Interface...")
    print("Access at: http://localhost:5003")
    print("This interface provides advanced AI research capabilities for the captions database")
    
    app.run(debug=True, host='0.0.0.0', port=5003)