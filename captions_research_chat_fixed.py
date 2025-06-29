#!/usr/bin/env python3
"""
Fixed Captions Database Research Chat Interface
Uses existing database structure and working search methods
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import anthropic
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'captions-research-secret-key')

# Initialize Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
try:
    client = anthropic.Anthropic(api_key=api_key) if api_key else None
    if client and api_key:
        print(f"✅ Anthropic client initialized successfully")
    else:
        print("❌ No Anthropic API key found")
        client = None
except Exception as e:
    client = None
    print(f"Anthropic client initialization failed: {e}")

def search_database_simple(query_terms: str) -> List[Dict]:
    """Simple database search that works with existing structure"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Use LIKE search for reliability
    search_words = query_terms.lower().split()
    like_conditions = []
    params = []
    
    for word in search_words:
        like_conditions.append("LOWER(c.text) LIKE ?")
        params.append(f"%{word}%")
    
    where_clause = " AND ".join(like_conditions)
    
    sql = f"""
        SELECT v.title, c.start_time, c.text, v.video_id
        FROM captions c
        JOIN videos v ON c.video_id = v.video_id
        WHERE {where_clause}
        ORDER BY v.title, CAST(c.start_time AS REAL)
        LIMIT 30
    """
    
    try:
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            # Convert start_time to seconds for URL
            try:
                start_seconds = int(float(row[1]))
            except:
                start_seconds = 0
                
            # Extract episode number from title if possible
            title = row[0]
            episode_num = None
            if "ep" in title.lower():
                import re
                match = re.search(r'ep(\d+)', title.lower())
                if match:
                    episode_num = int(match.group(1))
            
            results.append({
                'title': title,
                'episode_number': episode_num,
                'start_time': row[1],
                'start_seconds': start_seconds,
                'text': row[2],
                'video_id': row[3],
                'youtube_url': f"https://youtube.com/watch?v={row[3]}&t={start_seconds}s"
            })
        
        conn.close()
        return results
        
    except Exception as e:
        conn.close()
        print(f"Database search error: {e}")
        return []

@app.route('/')
def index():
    """Main research interface"""
    return render_template('captions_research_fixed.html')

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
            # Fallback to simple search
            search_results = search_database_simple(user_query)
            
            response_text = f"**Search Results for: {user_query}**\n\n"
            if search_results:
                for i, result in enumerate(search_results[:10], 1):
                    response_text += f"**{i}. {result['title']}**\n"
                    response_text += f"⏰ {result['start_time']}s - [Watch on YouTube]({result['youtube_url']})\n"
                    response_text += f"_{result['text'][:200]}..._\n\n"
            else:
                response_text += "No results found for your query."
            
            return jsonify({
                'response': response_text,
                'conversation_id': session.get('conversation_id', 'no-ai'),
                'timestamp': datetime.now().isoformat()
            })
        
        # Initialize conversation if new
        if 'conversation_id' not in session:
            session['conversation_id'] = str(uuid.uuid4())
        
        # First, do a database search
        search_results = search_database_simple(user_query)
        
        # Build context for Claude
        search_context = ""
        if search_results:
            search_context = "DATABASE SEARCH RESULTS:\n"
            for i, result in enumerate(search_results[:15], 1):
                search_context += f"{i}. {result['title']} (at {result['start_time']}s)\n"
                search_context += f"   Text: {result['text']}\n"
                search_context += f"   URL: {result['youtube_url']}\n\n"
        
        # Prepare conversation history for Claude
        messages = []
        for msg in conversation_history[-8:]:  # Keep last 8 messages for context
            messages.append({
                "role": "user" if msg['type'] == 'user' else "assistant",
                "content": msg['content']
            })
        
        # System prompt for Claude
        system_prompt = f"""You are an expert researcher analyzing C.S. Lewis biographical content from a comprehensive captions database. 

DATABASE CONTEXT:
- Contains 240+ videos from "Read on C. S. Lewis" series
- Full captions from Lewis biographical content
- Videos cover Lewis's diary entries, letters, and life events
- Database includes precise timestamps and YouTube links

YOUR TASK:
Analyze the search results and provide detailed research insights about: {user_query}

{search_context}

RESPONSE GUIDELINES:
- Provide specific episode references and timestamps
- Include exact quotes from the search results
- Generate YouTube URLs with timestamps
- Offer analytical insights and connections
- If multiple results exist, synthesize them into a comprehensive answer
- Suggest related research directions

ANSWER FORMAT:
- Start with key findings
- Include specific quotes and timestamps  
- Provide YouTube links
- End with research insights or suggestions

The user is asking: {user_query}"""

        messages.append({
            "role": "user", 
            "content": f"Please analyze these search results and provide detailed research insights about: {user_query}"
        })
        
        # Call Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            system=system_prompt,
            messages=messages
        )
        
        assistant_response = ""
        for block in response.content:
            if block.type == "text":
                assistant_response += block.text
        
        return jsonify({
            'response': assistant_response,
            'conversation_id': session['conversation_id'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def simple_search():
    """Simple search endpoint"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = search_database_simple(query)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Fixed Captions Database Research Chat Interface")
    print("Access at: http://localhost:5004")
    print("This interface provides AI research capabilities for the captions database")
    
    app.run(debug=True, host='0.0.0.0', port=5004)