#!/usr/bin/env python3
"""
Claude GitHub Search System - Autonomous Learning Database Search

This system:
1. Fetches latest context from GitHub repo
2. Provides comprehensive context to Claude API
3. Performs intelligent database searches
4. Documents successful patterns back to GitHub

Architecture: GitHub Context → Claude API → Database Search → Learning Documentation → GitHub Update
"""

import requests
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64
import anthropic
from flask import Flask, request, jsonify

app = Flask(__name__)

class GitHubClaudeSearchSystem:
    """Autonomous search system with GitHub learning loop"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'jeffpace')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', 'Sserf')
        self.db_path = 'captions.db'  # Local database copy
        
        # Initialize Anthropic client
        self.claude = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
    def fetch_latest_context_from_github(self) -> Dict[str, Any]:
        """Fetch all project resources from GitHub for Claude context"""
        
        print("🔄 Fetching latest context from GitHub...")
        
        context_package = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'repo': f"{self.repo_owner}/{self.repo_name}",
                'commit_sha': self._get_latest_commit_sha()
            },
            'core_files': {},
            'search_patterns': {},
            'learning_documents': {},
            'database_schema': {},
            'project_knowledge': {}
        }
        
        # Core project files to include
        core_files = [
            'CLAUDE.md',
            'README.md', 
            'intelligent_claude_search.py',
            'src/database/models.py',
            'THUMBNAIL_TEXT_EXTRACTION_PROTOCOL.md',
            'COMPREHENSIVE_AI_PROMPTING_GUIDE.md'
        ]
        
        # Learning documents (search findings)
        learning_files = [
            'lewis_admin_findings.md',
            'lewis_dreams_summary.md'
        ]
        
        # Search pattern examples
        search_pattern_files = [
            'search_movies.py',
            'search_lewis_admin.py', 
            'search_lewis_dreams.py',
            'episode_12_detailed.py'
        ]
        
        # Fetch core files
        for file_path in core_files:
            content = self._fetch_file_from_github(file_path)
            if content:
                context_package['core_files'][file_path] = content
                
        # Fetch learning documents
        for file_path in learning_files:
            content = self._fetch_file_from_github(file_path)
            if content:
                context_package['learning_documents'][file_path] = content
                
        # Fetch search patterns
        for file_path in search_pattern_files:
            content = self._fetch_file_from_github(file_path)
            if content:
                context_package['search_patterns'][file_path] = content
        
        # Add database schema info
        context_package['database_schema'] = self._extract_database_schema()
        
        # Add project knowledge summary
        context_package['project_knowledge'] = self._build_project_knowledge_summary(context_package)
        
        print(f"✅ Context package ready: {len(context_package['core_files'])} core files, {len(context_package['search_patterns'])} patterns, {len(context_package['learning_documents'])} learning docs")
        
        return context_package
    
    def _fetch_file_from_github(self, file_path: str) -> Optional[str]:
        """Fetch a single file from GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            headers = {'Authorization': f'token {self.github_token}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                return content
            else:
                print(f"⚠️  Could not fetch {file_path}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching {file_path}: {e}")
            return None
    
    def _get_latest_commit_sha(self) -> str:
        """Get latest commit SHA for context versioning"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits/main"
            headers = {'Authorization': f'token {self.github_token}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()['sha'][:7]
            return "unknown"
        except:
            return "unknown"
    
    def _extract_database_schema(self) -> Dict:
        """Extract database schema info for Claude context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Get sample data counts
            cursor.execute("SELECT COUNT(*) FROM videos")
            video_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM captions") 
            caption_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'tables': [table[0] for table in tables],
                'video_count': video_count,
                'caption_count': caption_count,
                'structure': 'videos (metadata) + captions (timed text segments)'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _build_project_knowledge_summary(self, context: Dict) -> Dict:
        """Build summary of project knowledge for Claude"""
        return {
            'purpose': 'C.S. Lewis YouTube caption database search system',
            'database_size': '240+ episodes with full-text searchable captions',
            'search_capabilities': 'Complex queries, timestamp links, episode targeting',
            'learning_system': 'Documents successful search patterns for future use',
            'claude_role': 'Intelligent database researcher with Lewis biographical knowledge'
        }
    
    def search_with_claude_api(self, user_query: str, context_package: Dict) -> Dict:
        """Send search request to Claude API with full context"""
        
        print(f"🧠 Sending query to Claude API: {user_query}")
        
        # Build comprehensive context prompt
        context_prompt = self._build_claude_context_prompt(context_package)
        
        # Create search prompt
        search_prompt = f"""
{context_prompt}

**USER SEARCH QUERY**: "{user_query}"

**YOUR TASK**: 
1. Search the captions database using your natural reasoning process
2. Apply the search methodologies from the context
3. Find the most relevant results with timestamps and YouTube links
4. Format results like your terminal searches
5. Return both the search results AND a pattern analysis

**IMPORTANT**: Use the database tools available to you to perform the actual search.
"""

        try:
            # Send to Claude API
            response = self.claude.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": search_prompt
                    }
                ],
                tools=[
                    {
                        "name": "database_query",
                        "description": "Query the captions database",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "sql": {"type": "string", "description": "SQL query to execute"},
                                "description": {"type": "string", "description": "What this query is trying to find"}
                            },
                            "required": ["sql", "description"]
                        }
                    }
                ]
            )
            
            # Process Claude's response
            return self._process_claude_response(response, user_query, context_package)
            
        except Exception as e:
            return {
                'error': f'Claude API error: {str(e)}',
                'fallback_search': self._fallback_database_search(user_query)
            }
    
    def _build_claude_context_prompt(self, context: Dict) -> str:
        """Build comprehensive context prompt for Claude"""
        
        prompt = f"""
# CLAUDE DATABASE SEARCH CONTEXT PACKAGE
**Version**: {context['metadata']['fetched_at']}
**Repo**: {context['metadata']['repo']} (commit: {context['metadata']['commit_sha']})

## PROJECT OVERVIEW
{context['core_files'].get('CLAUDE.md', 'Project instructions not available')}

## DATABASE SCHEMA
- **Videos Table**: {context['database_schema'].get('video_count', 0)} videos with metadata
- **Captions Table**: {context['database_schema'].get('caption_count', 0)} caption segments with timestamps
- **Structure**: videos(video_id, title) + captions(video_id, start_time, text)

## SEARCH METHODOLOGIES (from previous successful searches)
"""
        
        # Add learning documents
        for file_path, content in context['learning_documents'].items():
            prompt += f"\n### {file_path}\n{content[:500]}...\n"
        
        # Add search patterns
        prompt += "\n## SUCCESSFUL SEARCH PATTERNS\n"
        for file_path, content in context['search_patterns'].items():
            # Extract key SQL patterns
            if 'youtube.com/watch' in content:
                prompt += f"- YouTube URL pattern from {file_path}: youtube.com/watch?v={{video_id}}&t={{seconds}}s\n"
            if 'CAST(' in content and 'start_time' in content:
                prompt += f"- Timestamp conversion from {file_path}: Convert HH:MM:SS to seconds\n"
        
        prompt += f"""
## YOUR SEARCH CAPABILITIES
You have access to the captions database and should use your natural reasoning process to:
1. Understand the query context (Lewis biographical knowledge)
2. Try specific search combinations first
3. Expand to broader searches if needed
4. Build YouTube timestamp links for results
5. Format results with episode info and direct links

## LEARNING REQUIREMENT
After successful searches, document:
- What search strategy worked
- Key SQL patterns used
- Episode ranges that contained relevant content
- Specific terminology that matched
"""
        
        return prompt
    
    def _process_claude_response(self, response, user_query: str, context: Dict) -> Dict:
        """Process Claude's response and extract search results"""
        
        # Parse Claude's response for search results and patterns
        search_results = {
            'query': user_query,
            'results': [],
            'claude_analysis': '',
            'search_patterns_used': [],
            'success_metrics': {}
        }
        
        # Extract text response
        if hasattr(response, 'content') and response.content:
            search_results['claude_analysis'] = response.content[0].text if response.content else ''
        
        # Extract tool usage (database queries)
        if hasattr(response, 'tool_calls'):
            for tool_call in response.tool_calls:
                if tool_call.name == 'database_query':
                    sql = tool_call.input.get('sql', '')
                    description = tool_call.input.get('description', '')
                    
                    # Execute the query
                    db_results = self._execute_database_query(sql)
                    search_results['results'].extend(db_results)
                    search_results['search_patterns_used'].append({
                        'sql': sql,
                        'description': description,
                        'result_count': len(db_results)
                    })
        
        return search_results
    
    def _execute_database_query(self, sql: str) -> List[Dict]:
        """Execute database query and return formatted results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            conn.close()
            
            # Format results
            formatted_results = []
            for row in results:
                result = dict(zip(columns, row))
                
                # Add YouTube URL if we have video_id and start_time
                if 'video_id' in result and 'start_time' in result:
                    seconds = self._convert_timestamp_to_seconds(result['start_time'])
                    result['youtube_url'] = f"https://youtube.com/watch?v={result['video_id']}&t={seconds}s"
                
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _convert_timestamp_to_seconds(self, timestamp: str) -> int:
        """Convert HH:MM:SS.mmm to seconds"""
        try:
            parts = timestamp.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) 
            seconds = float(parts[2])
            return int(hours * 3600 + minutes * 60 + seconds)
        except:
            return 0
    
    def _fallback_database_search(self, query: str) -> List[Dict]:
        """Fallback search if Claude API fails"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple text search
            sql = """
                SELECT v.title, c.start_time, c.text, v.video_id
                FROM captions c
                JOIN videos v ON c.video_id = v.video_id
                WHERE LOWER(c.text) LIKE LOWER(?)
                ORDER BY v.title, CAST(c.start_time AS REAL)
                LIMIT 20
            """
            
            cursor.execute(sql, (f"%{query}%",))
            results = cursor.fetchall()
            
            formatted_results = []
            for row in results:
                seconds = self._convert_timestamp_to_seconds(row[1])
                formatted_results.append({
                    'title': row[0],
                    'start_time': row[1],
                    'text': row[2],
                    'video_id': row[3],
                    'youtube_url': f"https://youtube.com/watch?v={row[3]}&t={seconds}s"
                })
            
            conn.close()
            return formatted_results
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def document_successful_search(self, search_results: Dict) -> None:
        """Document successful search patterns back to GitHub"""
        
        if not search_results.get('results') or len(search_results['results']) < 3:
            print("⚠️  Search not successful enough to document")
            return
        
        print("📝 Documenting successful search pattern...")
        
        # Generate learning document
        learning_doc = self._generate_learning_document(search_results)
        
        # Create filename
        query_slug = search_results['query'].lower().replace(' ', '_').replace(',', '').replace('?', '')[:50]
        filename = f"search_learning_{datetime.now().strftime('%Y%m%d_%H%M')}_{query_slug}.md"
        
        # Push to GitHub
        self._push_learning_to_github(filename, learning_doc)
    
    def _generate_learning_document(self, search_results: Dict) -> str:
        """Generate a learning document from successful search"""
        
        doc = f"""# Search Learning: {search_results['query']}

**Generated**: {datetime.now().isoformat()}
**Results Found**: {len(search_results['results'])}

## Query Analysis
**Original Query**: "{search_results['query']}"

## Successful Search Patterns

### SQL Patterns Used
"""
        
        for pattern in search_results.get('search_patterns_used', []):
            doc += f"""
#### {pattern.get('description', 'Database Query')}
```sql
{pattern.get('sql', '')}
```
**Results**: {pattern.get('result_count', 0)} matches

"""
        
        doc += """
## Key Results Found

"""
        
        # Add top 5 results
        for i, result in enumerate(search_results['results'][:5]):
            if 'title' in result:
                doc += f"**{i+1}. {result['title']}**\n"
                doc += f"- Time: {result.get('start_time', 'N/A')}\n"
                doc += f"- Link: {result.get('youtube_url', 'N/A')}\n"
                doc += f"- Quote: {result.get('text', '')[:100]}...\n\n"
        
        doc += """
## Lessons Learned

### What Worked
- [Pattern analysis to be added by future searches]

### Episode Ranges
- [Episodes that contained relevant content]

### Search Strategy
- [Successful approach taken]

### For Future Searches
- [Recommendations for similar queries]
"""
        
        return doc
    
    def _push_learning_to_github(self, filename: str, content: str) -> bool:
        """Push learning document to GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/search_learnings/{filename}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Content-Type': 'application/json'
            }
            
            # Encode content
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                'message': f'🧠 Document successful search pattern: {filename}',
                'content': encoded_content,
                'branch': 'main'
            }
            
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [201, 200]:
                print(f"✅ Learning document pushed to GitHub: {filename}")
                return True
            else:
                print(f"❌ Failed to push learning document: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error pushing to GitHub: {e}")
            return False

# Flask API endpoints
search_system = GitHubClaudeSearchSystem()

@app.route('/api/github-claude-search', methods=['POST'])
def github_claude_search():
    """Main search endpoint with GitHub learning loop"""
    
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({'error': 'Query required'}), 400
        
        # Step 1: Fetch latest context from GitHub
        context_package = search_system.fetch_latest_context_from_github()
        
        # Step 2: Search with Claude API
        search_results = search_system.search_with_claude_api(user_query, context_package)
        
        # Step 3: Document successful patterns
        if search_results.get('results'):
            search_system.document_successful_search(search_results)
        
        # Step 4: Return results
        return jsonify({
            'query': user_query,
            'results': search_results,
            'context_version': context_package['metadata']['commit_sha'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/context-status', methods=['GET'])
def context_status():
    """Check GitHub context package status"""
    try:
        context = search_system.fetch_latest_context_from_github()
        return jsonify({
            'status': 'ready',
            'files_loaded': len(context['core_files']),
            'learning_docs': len(context['learning_documents']),
            'search_patterns': len(context['search_patterns']),
            'last_commit': context['metadata']['commit_sha']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Claude GitHub Search System Starting...")
    print("🔗 GitHub Learning Loop: Fetch Context → Claude Search → Document Patterns → Update Repo")
    print("🌐 Access at: http://localhost:5008")
    
    app.run(debug=True, host='0.0.0.0', port=5008)