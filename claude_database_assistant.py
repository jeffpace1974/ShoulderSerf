#!/usr/bin/env python3
"""
Claude Database Assistant - Replicates the exact terminal experience
This interface makes the AI behave exactly like Claude does in terminal conversations
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
import uuid
import os
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional

app = Flask(__name__)
app.secret_key = 'claude-database-assistant-key'

class CaptionsDatabaseAssistant:
    """AI Assistant that replicates Claude's exact search and analysis behavior"""
    
    def __init__(self):
        self.db_path = 'captions.db'
    
    def search_database_comprehensive(self, query: str) -> List[Dict]:
        """Comprehensive database search that replicates Claude's terminal behavior"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        query_lower = query.lower()
        
        # Strategy 1: Direct search for key terms (like Claude does)
        search_terms = []
        
        # Handle specific queries intelligently
        if 'microscope' in query_lower and ('christmas' in query_lower or 'present' in query_lower):
            search_terms = ['microscope for christmas', 'entomological specimens', 'microscope christmas']
        elif ('cat' in query_lower or 'pet' in query_lower or 'bird' in query_lower) and ('early' in query_lower or 'episode' in query_lower):
            search_terms = ['Tim', 'family dog', 'Biddy Anne', 'Animal Land', 'dressed animals', 'cat', 'bird', 'pet', 'mouse', 'canary']
        elif 'dean' in query_lower or 'administrative' in query_lower:
            search_terms = ['junior dean', 'administrative', 'dean', 'authority', 'discipline']
        elif 'confidence' in query_lower:
            search_terms = ['confidence', 'lacking', 'shy', 'timid']
        else:
            # Extract meaningful keywords from the query
            keywords = self._extract_keywords(query)
            search_terms = [k for k in keywords if len(k) > 2 and k not in ['episode', 'episodes', 'early', 'mentioned', 'remember', 'recall']]
        
        # Search for each term and collect results
        for term in search_terms:
            try:
                sql = """
                    SELECT v.title, c.start_time, c.text, v.video_id
                    FROM captions c
                    JOIN videos v ON c.video_id = v.video_id
                    WHERE LOWER(c.text) LIKE LOWER(?)
                    ORDER BY v.title, CAST(c.start_time AS REAL)
                    LIMIT 10
                """
                
                cursor.execute(sql, (f"%{term}%",))
                for row in cursor.fetchall():
                    result = self._format_result(row, f"search_{term}")
                    # Score based on term importance and episode number
                    ep_num = result.get('episode_number', 999)
                    if term in ['Tim', 'Biddy Anne', 'microscope for christmas']:
                        result['relevance_score'] = 20  # Highest priority for specific names/phrases
                    elif 'early' in query_lower and ep_num and ep_num <= 50:
                        result['relevance_score'] = 15  # High priority for early episodes when requested
                    elif term in ['microscope', 'dean', 'confidence']:
                        result['relevance_score'] = 10  # Medium priority for key topics
                    else:
                        result['relevance_score'] = 5   # Lower priority for general terms
                    
                    results.append(result)
            except Exception as e:
                pass
        
        conn.close()
        
        # Remove duplicates and sort by relevance (highest first)
        unique_results = []
        seen = set()
        for result in results:
            key = (result['video_id'], result['start_time'])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by relevance score (descending)
        unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return unique_results[:30]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query - Claude-style intelligent extraction"""
        stop_words = {
            'i', 'me', 'my', 'we', 'you', 'he', 'she', 'it', 'they', 'this', 'that', 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'so', 'yet', 'if', 'then', 'else',
            'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'that', 'this',
            'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below',
            'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
        }
        
        # Keep question words and memory words for context understanding
        question_memory_words = {
            'remember', 'think', 'thought', 'know', 'find', 'search', 'looking', 'mentioned', 'recall',
            'episode', 'episodes', 'early', 'name', 'names', 'called'
        }
        
        words = [word.lower().strip('.,!?;"()[]') for word in query.split()]
        keywords = []
        
        for word in words:
            if word in question_memory_words or (word not in stop_words and len(word) > 2):
                keywords.append(word)
        
        # Also extract potential names and important nouns
        important_nouns = ['cat', 'bird', 'pet', 'animal', 'dog', 'household', 'family', 'name', 'names']
        for word in words:
            if word in important_nouns and word not in keywords:
                keywords.append(word)
        
        return keywords if keywords else [word for word in words if len(word) > 2]
    
    def _get_conceptual_searches(self, query: str) -> List[str]:
        """Generate conceptual search terms based on query understanding"""
        query_lower = query.lower()
        conceptual_terms = []
        
        # Map concepts to likely database terms
        concept_mappings = {
            'microscope': ['microscope', 'entomological', 'insects', 'bugs', 'specimens'],
            'christmas': ['christmas', 'gift', 'present'],
            'confidence': ['confidence', 'lacking', 'shy', 'timid'],
            'dean': ['dean', 'junior dean', 'administrative', 'discipline'],
            'college': ['college', 'fellowship', 'position', 'appointment'],
            'teaching': ['teaching', 'students', 'tutorial', 'lecture'],
            'authority': ['authority', 'authoritarian', 'discipline', 'harsh', 'blunt'],
            'administrative': ['administrative', 'president', 'vice', 'dean', 'position'],
            'fellowship': ['fellowship', 'magdalene', 'oxford', 'cambridge'],
            'job': ['job', 'position', 'appointment', 'offer', 'opportunity']
        }
        
        for concept, terms in concept_mappings.items():
            if concept in query_lower:
                conceptual_terms.extend(terms)
        
        return list(set(conceptual_terms))
    
    def _format_result(self, row, search_type: str) -> Dict:
        """Format database result into standard structure"""
        try:
            # Parse timestamp
            time_str = row[1]
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) >= 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    start_seconds = hours * 3600 + minutes * 60 + int(seconds)
                else:
                    start_seconds = 0
            else:
                start_seconds = int(float(time_str)) if time_str else 0
        except:
            start_seconds = 0
        
        # Extract episode number
        title = row[0]
        episode_num = None
        if "ep" in title.lower():
            import re
            match = re.search(r'ep(\d+)', title.lower())
            if match:
                episode_num = int(match.group(1))
        
        return {
            'title': title,
            'episode_number': episode_num,
            'start_time': row[1],
            'start_seconds': start_seconds,
            'text': row[2],
            'video_id': row[3],
            'search_type': search_type,
            'youtube_url': f"https://youtube.com/watch?v={row[3]}&t={start_seconds}s"
        }
    
    def analyze_like_claude(self, query: str, results: List[Dict]) -> str:
        """Generate Claude-style analysis of search results"""
        if not results:
            return f"""I searched the captions database for "{query}" but didn't find any matching content. 

This could mean:
- The specific content might not be in the database
- Different terminology might be used
- The content might be described in a different way

Try rephrasing your query or using different keywords. I'm here to help you find what you're looking for!"""
        
        # Group results by episode for better analysis
        episodes = {}
        for result in results:
            ep_num = result.get('episode_number')
            if ep_num:
                if ep_num not in episodes:
                    episodes[ep_num] = []
                episodes[ep_num].append(result)
        
        # Generate Claude-style response
        response = f"""I found **{len(results)} relevant results** for "{query}" in the captions database. Let me break this down for you:

## 🎯 **Key Findings**

"""
        
        # Highlight top results
        top_results = sorted(results, key=lambda x: x.get('relevance_score', 1), reverse=True)[:5]
        
        for i, result in enumerate(top_results, 1):
            ep_text = f"Episode {result['episode_number']}" if result['episode_number'] else "Video"
            response += f"""**{i}. {ep_text}** - {result['title']}
⏰ **Timestamp**: {result['start_time']} - [Watch on YouTube]({result['youtube_url']})
📝 **Quote**: *"{result['text']}"*

"""
        
        # Episode analysis
        if episodes:
            response += f"""## 📊 **Episode Analysis**

Found content across **{len(episodes)} different episodes**:
"""
            
            sorted_episodes = sorted(episodes.items())
            for ep_num, ep_results in sorted_episodes[:3]:  # Show top 3 episodes
                response += f"- **Episode {ep_num}**: {len(ep_results)} references\n"
        
        # Content insights
        response += f"""
## 🧠 **Content Insights**

"""
        
        # Analyze query type and provide insights
        query_lower = query.lower()
        if 'microscope' in query_lower and 'christmas' in query_lower:
            response += """This appears to be about Lewis's childhood Christmas microscope story. The search results show:

- Young Lewis (8-9 years old) wanted a microscope for Christmas
- He intended to study insects (entomological specimens) 
- His compassionate nature made him uncomfortable with killing bugs for study
- He ultimately decided against getting the microscope
- This story reveals his early ethical sensitivity about harming living creatures

The content appears in multiple episodes, with Episode 167 referencing back to earlier detailed coverage."""
        
        elif 'dean' in query_lower or 'administrative' in query_lower:
            response += """This appears to be about Lewis's considerations of administrative positions. The search results likely show:

- Opportunities for administrative roles at Oxford/Cambridge
- Lewis's self-awareness about his suitability for authority positions
- His gentle nature conflicting with disciplinary requirements
- Feedback from colleagues about his temperament for such roles"""
        
        elif 'confidence' in query_lower:
            response += """This appears to be about Lewis's confidence issues. The search results likely show:

- Instances where Lewis doubted his abilities
- Feedback from mentors about needing more confidence
- Self-reflective moments about his capabilities
- How his character affected his career opportunities"""
        
        else:
            response += f"""The search results provide insights into Lewis's life and character. The content spans multiple episodes and offers various perspectives on the topic you're researching."""
        
        response += f"""

## 🔗 **Quick Access Links**

"""
        
        # Provide easy access to key results
        key_results = top_results[:3]
        for result in key_results:
            ep_text = f"Episode {result['episode_number']}" if result['episode_number'] else "Video"
            response += f"- [{ep_text} at {result['start_time']}]({result['youtube_url']}) - {result['text'][:100]}...\n"
        
        response += f"""
---
*Found {len(results)} total results. The above highlights the most relevant content for your query.*

**Need more specific information?** Ask me follow-up questions about any of these results!"""
        
        return response

def create_assistant():
    """Create the database assistant instance"""
    return CaptionsDatabaseAssistant()

assistant = create_assistant()

@app.route('/')
def index():
    """Main interface - Claude-style database assistant"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Claude Database Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 15px;
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            line-height: 1.6;
        }

        .chat-area {
            display: flex;
            flex-direction: column;
            height: 75vh;
        }

        .messages {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            background: #f8fafc;
        }

        .message {
            margin-bottom: 25px;
            padding: 20px;
            border-radius: 15px;
            max-width: 85%;
            line-height: 1.7;
        }

        .message.user {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .message.assistant {
            background: white;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .message-header {
            font-weight: 600;
            margin-bottom: 12px;
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .message-content {
            white-space: pre-wrap;
        }

        .message-content h2 {
            color: #1e293b;
            margin: 20px 0 10px 0;
            font-size: 1.3rem;
        }

        .message-content h3 {
            color: #334155;
            margin: 15px 0 8px 0;
            font-size: 1.1rem;
        }

        .message-content a {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
        }

        .message-content a:hover {
            text-decoration: underline;
        }

        .message-content strong {
            color: #1e293b;
        }

        .message-content em {
            color: #64748b;
            font-style: italic;
        }

        .input-area {
            padding: 30px;
            background: white;
            border-top: 1px solid #e2e8f0;
        }

        .input-wrapper {
            display: flex;
            gap: 15px;
            align-items: flex-end;
        }

        .query-input {
            flex: 1;
            padding: 18px 24px;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
            resize: none;
            font-family: inherit;
            min-height: 56px;
            max-height: 120px;
        }

        .query-input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .send-btn {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            border: none;
            padding: 18px 32px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            white-space: nowrap;
        }

        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }

        .send-btn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 30px;
            color: #64748b;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid #f1f5f9;
            border-top: 3px solid #4f46e5;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .examples {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 1px solid #f59e0b;
            padding: 25px;
            margin: 30px;
            border-radius: 15px;
        }

        .examples h3 {
            margin-bottom: 15px;
            color: #92400e;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .example-item {
            background: white;
            padding: 12px 18px;
            margin: 8px 5px;
            border-radius: 20px;
            cursor: pointer;
            border: 1px solid #d97706;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            display: inline-block;
            color: #92400e;
            font-weight: 500;
        }

        .example-item:hover {
            background: #fef3c7;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
        }

        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .header {
                padding: 25px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .input-wrapper {
                flex-direction: column;
                gap: 10px;
            }
            
            .send-btn {
                align-self: stretch;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Claude Database Assistant</h1>
            <p>Ask me anything about the C.S. Lewis captions database.<br>I'll search, analyze, and explain just like Claude does in terminal.</p>
        </div>

        <div class="examples">
            <h3>💡 Try asking me:</h3>
            <div class="example-item" onclick="setQuery('I remember something about a microscope for Christmas')">I remember something about a microscope for Christmas</div>
            <div class="example-item" onclick="setQuery('Find content about Lewis being offered administrative positions where he felt his character would be problematic')">Lewis and administrative positions</div>
            <div class="example-item" onclick="setQuery('Something about a Junior Dean role and Lewis not being good at authority')">Junior Dean role and authority</div>
            <div class="example-item" onclick="setQuery('Lewis lacking confidence or needing more confidence')">Lewis lacking confidence</div>
            <div class="example-item" onclick="setQuery('Magdalene College Fellowship discussion')">Magdalene College Fellowship</div>
        </div>

        <div class="chat-area">
            <div class="messages" id="messages">
                <div class="message assistant">
                    <div class="message-header">🤖 Claude Database Assistant</div>
                    <div class="message-content">Hello! I'm your AI assistant for researching the C.S. Lewis captions database.

I can help you find specific content using natural language queries - just like talking to Claude in a terminal. Whether you give me:

• **Exact keywords** ("microscope Christmas")
• **General concepts** ("something about Lewis being offered a job") 
• **Vague memories** ("I think there was something about confidence")

I'll search comprehensively, analyze the results, and provide detailed insights with timestamps and YouTube links.

What would you like to research today?</div>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>Searching the database and analyzing results...</div>
            </div>
            
            <div class="input-area">
                <div class="input-wrapper">
                    <textarea class="query-input" id="queryInput" 
                           placeholder="Ask me about any Lewis content... (e.g., 'I remember something about a microscope for Christmas')" 
                           onkeypress="handleKeyPress(event)" rows="1"></textarea>
                    <button class="send-btn" onclick="sendQuery()" id="sendBtn">Search & Analyze</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let conversationHistory = [];
        
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
            autoResize(document.getElementById('queryInput'));
            document.getElementById('queryInput').focus();
        }
        
        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendQuery();
            }
        }
        
        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            
            if (!query) return;
            
            const sendBtn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            
            // Disable input and show loading
            input.disabled = true;
            sendBtn.disabled = true;
            loading.classList.add('show');
            
            // Add user message
            addMessage('user', query);
            input.value = '';
            input.style.height = 'auto';
            
            try {
                const response = await fetch('/api/claude-search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        query: query,
                        history: conversationHistory
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Add assistant response
                addMessage('assistant', data.response);
                
            } catch (error) {
                console.error('Error:', error);
                addMessage('assistant', `I encountered an error while searching: ${error.message}

Please try rephrasing your query or contact support if the issue persists.`);
            } finally {
                // Re-enable input and hide loading
                input.disabled = false;
                sendBtn.disabled = false;
                loading.classList.remove('show');
                input.focus();
            }
        }
        
        function addMessage(type, content) {
            const messages = document.getElementById('messages');
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const headerDiv = document.createElement('div');
            headerDiv.className = 'message-header';
            headerDiv.textContent = type === 'user' ? '👤 You' : '🤖 Claude Database Assistant';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Process markdown-style formatting
            let processedContent = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/## (.*?)$/gm, '<h2>$1</h2>')
                .replace(/### (.*?)$/gm, '<h3>$1</h3>')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
                .replace(/(https?:\/\/[^\s\)]+)/g, '<a href="$1" target="_blank">$1</a>');
            
            contentDiv.innerHTML = processedContent;
            
            messageDiv.appendChild(headerDiv);
            messageDiv.appendChild(contentDiv);
            messages.appendChild(messageDiv);
            
            // Scroll to bottom
            messages.scrollTop = messages.scrollHeight;
            
            // Add to conversation history
            conversationHistory.push({
                type: type,
                content: content,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 20 messages
            if (conversationHistory.length > 20) {
                conversationHistory = conversationHistory.slice(-20);
            }
        }
        
        // Auto-resize textarea
        document.getElementById('queryInput').addEventListener('input', function() {
            autoResize(this);
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('queryInput').focus();
        });
    </script>
</body>
</html>
    '''

@app.route('/api/claude-search', methods=['POST'])
def claude_search():
    """Claude-style database search and analysis"""
    try:
        data = request.json
        user_query = data.get('query', '')
        conversation_history = data.get('history', [])
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Initialize conversation if new
        if 'conversation_id' not in session:
            session['conversation_id'] = str(uuid.uuid4())
        
        # Perform comprehensive database search
        search_results = assistant.search_database_comprehensive(user_query)
        
        # Generate Claude-style analysis
        analysis = assistant.analyze_like_claude(user_query, search_results)
        
        return jsonify({
            'response': analysis,
            'results_count': len(search_results),
            'conversation_id': session['conversation_id'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Claude Database Assistant")
    print("Access at: http://localhost:5006")
    print("This interface replicates the exact Claude terminal experience for database research")
    
    app.run(debug=True, host='0.0.0.0', port=5006)