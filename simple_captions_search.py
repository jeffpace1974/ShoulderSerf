#!/usr/bin/env python3
"""
Simple Captions Database Search Interface
Basic search functionality without AI integration
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)

def search_database(query_terms, episode_filter=None):
    """Simple database search"""
    conn = sqlite3.connect('captions.db')
    cursor = conn.cursor()
    
    # Build search query
    search_terms = []
    for term in query_terms.split():
        search_terms.append(f'"{term}"')
    search_query = ' OR '.join(search_terms)
    
    if episode_filter:
        if "before" in episode_filter.lower():
            ep_num = int(''.join(filter(str.isdigit, episode_filter)))
            sql = """
                SELECT v.episode_number, v.title, cs.start_time, cs.text, v.video_id
                FROM caption_segments cs
                JOIN videos v ON cs.video_id = v.video_id
                WHERE v.episode_number < ? AND cs.text MATCH ?
                ORDER BY v.episode_number, cs.start_time
                LIMIT 50
            """
            cursor.execute(sql, (ep_num, search_query))
        else:
            ep_num = int(''.join(filter(str.isdigit, episode_filter)))
            sql = """
                SELECT v.episode_number, v.title, cs.start_time, cs.text, v.video_id
                FROM caption_segments cs
                JOIN videos v ON cs.video_id = v.video_id
                WHERE v.episode_number = ? AND cs.text MATCH ?
                ORDER BY cs.start_time
                LIMIT 50
            """
            cursor.execute(sql, (ep_num, search_query))
    else:
        sql = """
            SELECT v.episode_number, v.title, cs.start_time, cs.text, v.video_id
            FROM caption_segments cs
            JOIN videos v ON cs.video_id = v.video_id
            WHERE cs.text MATCH ?
            ORDER BY v.episode_number, cs.start_time
            LIMIT 50
        """
        cursor.execute(sql, (search_query,))
    
    results = []
    for row in cursor.fetchall():
        # Convert seconds to readable timestamp
        start_time = int(row[2])
        hours = start_time // 3600
        minutes = (start_time % 3600) // 60
        seconds = start_time % 60
        
        if hours > 0:
            timestamp = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            timestamp = f"{minutes}:{seconds:02d}"
            
        results.append({
            'episode_number': row[0],
            'title': row[1],
            'start_time': row[2],
            'timestamp': timestamp,
            'text': row[3],
            'video_id': row[4],
            'youtube_url': f"https://youtube.com/watch?v={row[4]}&t={start_time}s"
        })
    
    conn.close()
    return results

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Captions Search</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .search-box { margin: 20px 0; }
            .search-box input { padding: 10px; width: 400px; font-size: 16px; }
            .search-box button { padding: 10px 20px; font-size: 16px; }
            .result { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .episode { font-weight: bold; color: #2196F3; }
            .timestamp { color: #666; font-size: 14px; }
            .text { margin: 10px 0; line-height: 1.5; }
            .youtube-link { color: #FF0000; text-decoration: none; }
            .example { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🔍 Simple Captions Database Search</h1>
        <p>Search the C.S. Lewis captions database for specific content.</p>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Enter search terms (e.g., microscope Christmas)" onkeypress="handleKeyPress(event)">
            <button onclick="search()">Search</button>
        </div>
        
        <div class="example">
            <strong>Examples:</strong><br>
            • microscope Christmas<br>
            • Junior Dean administrative<br>
            • confidence lacking<br>
            • Magdalene College Fellowship
        </div>
        
        <div id="results"></div>
        
        <script>
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    search();
                }
            }
            
            async function search() {
                const query = document.getElementById('searchInput').value.trim();
                if (!query) return;
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '<p>Searching...</p>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const data = await response.json();
                    
                    if (data.results.length === 0) {
                        resultsDiv.innerHTML = '<p>No results found.</p>';
                        return;
                    }
                    
                    let html = `<h3>Found ${data.results.length} results:</h3>`;
                    
                    data.results.forEach(result => {
                        html += `
                            <div class="result">
                                <div class="episode">Episode ${result.episode_number}: ${result.title}</div>
                                <div class="timestamp">⏰ ${result.timestamp} - <a href="${result.youtube_url}" target="_blank" class="youtube-link">Watch on YouTube</a></div>
                                <div class="text">${result.text}</div>
                            </div>
                        `;
                    });
                    
                    resultsDiv.innerHTML = html;
                    
                } catch (error) {
                    resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = search_database(query)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Simple Captions Search Interface")
    print("Access at: http://localhost:5004")
    app.run(debug=True, host='0.0.0.0', port=5004)