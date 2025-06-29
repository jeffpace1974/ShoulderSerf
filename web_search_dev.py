#!/usr/bin/env python3
"""
Web-based search interface for C.S. Lewis caption database.

A Flask web application that provides an intuitive search interface
for exploring the scraped YouTube caption database.
"""

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
import os
import sys
from datetime import datetime
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import CaptionDatabase
from src.search.concept_analyzer import ConceptAnalyzer

app = Flask(__name__, template_folder='templates_dev')
app.secret_key = 'sserf-lewis-search-dev-key'

# Initialize database and concept analyzer
db = CaptionDatabase()
concept_analyzer = ConceptAnalyzer()

def format_time(time_str):
    """Convert time string to more readable format."""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                s = float(s)
                return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    except:
        pass
    return time_str

def get_youtube_url(video_id, start_time=None):
    """Generate YouTube URL with optional timestamp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    if start_time:
        try:
            # Convert start_time to seconds for YouTube URL
            if ':' in start_time:
                parts = start_time.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    total_seconds = int(h) * 3600 + int(m) * 60 + int(float(s))
                    url += f"&t={total_seconds}s"
                elif len(parts) == 2:
                    m, s = parts
                    total_seconds = int(m) * 60 + int(float(s))
                    url += f"&t={total_seconds}s"
        except:
            pass
    return url

@app.route('/')
def index():
    """Main search page."""
    stats = db.get_statistics()
    return render_template('search.html', stats=stats)

@app.route('/search')
def search():
    """Search endpoint."""
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if not query:
            return jsonify({'results': [], 'total': 0, 'pages': 0, 'current_page': page, 'error': None})
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Use enhanced search that includes thumbnails, tags, and playlists
        search_limit = per_page * 10  # Get more results for accurate pagination
        all_results = db.search_enhanced(query, search_limit)
        
        # Calculate pagination
        total_results = len(all_results)
        total_pages = math.ceil(total_results / per_page)
        
        # Slice results for current page
        start_idx = offset
        end_idx = start_idx + per_page
        page_results = all_results[start_idx:end_idx]
        
        # Format results for display
        formatted_results = []
        for result in page_results:
            formatted_result = {
                'video_id': result['video_id'],
                'title': result['title'],
                'uploader': result['uploader'],
                'upload_date': result['upload_date'],
                'start_time': format_time(result['start_time']) if result.get('start_time') else None,
                'end_time': format_time(result['end_time']) if result.get('end_time') else None,
                'text': result['text'] if result.get('text') else '',
                'thumbnail': result.get('thumbnail'),
                'thumbnail_text': result.get('thumbnail_text'),
                'tags': result.get('tags', []),
                'playlists': result.get('playlists', []),
                'match_type': result.get('match_type', 'caption'),
                'youtube_url': get_youtube_url(result['video_id'], result.get('start_time')),
                'youtube_url_plain': get_youtube_url(result['video_id'])
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'results': formatted_results,
            'total': total_results,
            'pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'query': query,
            'error': None
        })
        
    except Exception as e:
        # Return JSON error response instead of HTML error page
        return jsonify({
            'results': [],
            'total': 0,
            'pages': 0,
            'current_page': 1,
            'per_page': 20,
            'query': query if 'query' in locals() else '',
            'error': f'Search failed: {str(e)}'
        }), 500

@app.route('/video/<video_id>')
def video_detail(video_id):
    """Show all captions for a specific video."""
    video_info = db.get_video_info(video_id)
    if not video_info:
        return "Video not found", 404
    
    captions = db.get_video_captions(video_id)
    
    # Format captions
    formatted_captions = []
    for caption in captions:
        formatted_captions.append({
            'start_time': format_time(caption['start_time']),
            'end_time': format_time(caption['end_time']),
            'text': caption['text'],
            'youtube_url': get_youtube_url(video_id, caption['start_time'])
        })
    
    return render_template('video_detail.html', 
                         video=video_info, 
                         captions=formatted_captions,
                         youtube_url=get_youtube_url(video_id))

@app.route('/concept-search')
def concept_search():
    """AI-powered conceptual search endpoint."""
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        model = request.args.get('model', None)  # New model parameter
        
        if not query:
            return jsonify({
                'results': [], 
                'total': 0, 
                'pages': 0, 
                'current_page': page, 
                'error': None,
                'analysis': None,
                'search_type': 'concept'
            })
        
        # Analyze the conceptual query with specified model
        analysis = concept_analyzer.analyze_concept_query(query, model)
        
        # Generate multiple search strategies
        search_queries = concept_analyzer.generate_search_queries(analysis)
        
        # Perform searches with each strategy using enhanced search
        all_results = []
        seen_results = set()  # Track unique results by video_id + text
        
        for search_query in search_queries:
            search_results = db.search_enhanced(search_query, per_page * 3)
            
            # Deduplicate results
            for result in search_results:
                result_key = f"{result['video_id']}_{result['text'][:50]}"
                if result_key not in seen_results:
                    seen_results.add(result_key)
                    all_results.append(result)
        
        # Rank results by conceptual relevance
        ranked_results = concept_analyzer.rank_results(all_results, analysis, query)
        
        # Apply pagination
        total_results = len(ranked_results)
        total_pages = math.ceil(total_results / per_page) if total_results > 0 else 0
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_results = ranked_results[start_idx:end_idx]
        
        # Format results for display
        formatted_results = []
        for result in page_results:
            formatted_result = {
                'video_id': result['video_id'],
                'title': result['title'],
                'uploader': result['uploader'],
                'upload_date': result['upload_date'],
                'start_time': format_time(result['start_time']) if result.get('start_time') else None,
                'end_time': format_time(result['end_time']) if result.get('end_time') else None,
                'text': result['text'] if result.get('text') else '',
                'thumbnail': result.get('thumbnail'),
                'thumbnail_text': result.get('thumbnail_text'),
                'tags': result.get('tags', []),
                'playlists': result.get('playlists', []),
                'match_type': result.get('match_type', 'caption'),
                'concept_score': result.get('concept_score', 0),
                'youtube_url': get_youtube_url(result['video_id'], result.get('start_time')),
                'youtube_url_plain': get_youtube_url(result['video_id'])
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'results': formatted_results,
            'total': total_results,
            'pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'query': query,
            'error': None,
            'analysis': analysis,
            'search_type': 'concept',
            'search_queries': search_queries
        })
        
    except Exception as e:
        return jsonify({
            'results': [],
            'total': 0,
            'pages': 0,
            'current_page': 1,
            'per_page': 20,
            'query': query if 'query' in locals() else '',
            'error': f'Concept search failed: {str(e)}',
            'search_type': 'concept'
        }), 500

@app.route('/stats')
def stats():
    """Database statistics API endpoint."""
    return jsonify(db.get_statistics())

@app.route('/models')
def models():
    """Available AI models endpoint."""
    return jsonify(concept_analyzer.get_available_models())

@app.route('/static/assets/<filename>')
def serve_assets(filename):
    """Serve static asset files."""
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'assets'), filename)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates_dev', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5001)