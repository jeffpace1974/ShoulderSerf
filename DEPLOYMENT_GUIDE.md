# Claude GitHub Search System - Deployment Guide

## Overview
This guide explains how to deploy the autonomous Claude search system that learns from GitHub and updates patterns automatically.

## Architecture

```
Frontend (Web UI) → API Server → GitHub Context Fetcher → Claude API → Database → Learning Documentation → GitHub Update
                                         ↑                                                                    ↓
                                         ←─────────────── Autonomous Learning Loop ──────────────────→
```

## Prerequisites

### Required Accounts & Keys
1. **GitHub Personal Access Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create token with `repo` permissions
   - Save as `GITHUB_TOKEN` environment variable

2. **Anthropic API Key**
   - Sign up at console.anthropic.com
   - Create API key
   - Save as `ANTHROPIC_API_KEY` environment variable

3. **Local Database**
   - Ensure `captions.db` is available locally
   - Or configure cloud database connection

### Required Dependencies
```bash
pip install flask anthropic requests python-dotenv
```

## Local Development Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your credentials
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
GITHUB_REPO_OWNER=jeffpace
GITHUB_REPO_NAME=Sserf
```

### 2. Start the System
```bash
python claude_github_search_system.py
```

### 3. Test the API
```bash
# Test context loading
curl http://localhost:5008/api/context-status

# Test search
curl -X POST http://localhost:5008/api/github-claude-search \
  -H "Content-Type: application/json" \
  -d '{"query": "Lewis writing about his father and money troubles"}'
```

## Cloud Deployment Options

### Option 1: Heroku Deployment

#### 1. Create Heroku App
```bash
heroku create your-claude-search-app
```

#### 2. Set Environment Variables
```bash
heroku config:set GITHUB_TOKEN=your_token
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set GITHUB_REPO_OWNER=jeffpace
heroku config:set GITHUB_REPO_NAME=Sserf
```

#### 3. Deploy
```bash
git add .
git commit -m "Deploy Claude GitHub Search System"
git push heroku main
```

### Option 2: AWS Lambda + API Gateway

#### 1. Package Dependencies
```bash
pip install -r requirements.txt -t ./package
cp claude_github_search_system.py ./package/
```

#### 2. Create Lambda Function
- Upload package as ZIP
- Set handler to `claude_github_search_system.lambda_handler`
- Configure environment variables
- Set timeout to 5 minutes

#### 3. Configure API Gateway
- Create REST API
- Connect to Lambda function
- Enable CORS
- Deploy to stage

### Option 3: Google Cloud Run

#### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5008

CMD ["python", "claude_github_search_system.py"]
```

#### 2. Build and Deploy
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/claude-search
gcloud run deploy --image gcr.io/PROJECT_ID/claude-search --platform managed
```

## Database Configuration

### Local SQLite (Development)
```python
DATABASE_PATH=captions.db
```

### Cloud Database (Production)
For production, consider:

#### PostgreSQL on AWS RDS
```python
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

#### MySQL on Google Cloud SQL
```python
DATABASE_URL=mysql://user:pass@host:3306/dbname
```

#### Upload captions.db to Cloud Storage
```bash
# AWS S3
aws s3 cp captions.db s3://your-bucket/captions.db

# Google Cloud Storage
gsutil cp captions.db gs://your-bucket/captions.db
```

## GitHub Repository Setup

### 1. Create Learning Directory
```bash
mkdir search_learnings
git add search_learnings/
git commit -m "Add learning directory for autonomous pattern documentation"
```

### 2. Verify GitHub Token Permissions
Test the token can read and write to your repository:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/jeffpace/Sserf/contents/README.md
```

### 3. Set Up Webhook (Optional)
For real-time context updates, configure GitHub webhook:
- Go to Repository Settings → Webhooks
- Add webhook pointing to your deployed API
- Listen for `push` events to `main` branch

## Frontend Integration

### Simple HTML Interface
```html
<!DOCTYPE html>
<html>
<head>
    <title>Claude GitHub Search</title>
</head>
<body>
    <h1>🧠 Claude Search with GitHub Learning</h1>
    <input type="text" id="query" placeholder="Enter your search query">
    <button onclick="search()">Search</button>
    <div id="results"></div>

    <script>
    async function search() {
        const query = document.getElementById('query').value;
        const response = await fetch('/api/github-claude-search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query})
        });
        const data = await response.json();
        document.getElementById('results').innerHTML = 
            '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    }
    </script>
</body>
</html>
```

### React Frontend
```jsx
import React, { useState } from 'react';

function ClaudeSearch() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/github-claude-search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            });
            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>🧠 Claude GitHub Search</h1>
            <input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter search query"
            />
            <button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>
            {results && (
                <div>
                    <h3>Results ({results.results?.results?.length || 0})</h3>
                    <pre>{JSON.stringify(results, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}
```

## Monitoring & Maintenance

### Health Checks
```bash
# API health
curl http://your-domain/api/context-status

# GitHub connectivity
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/jeffpace/Sserf

# Claude API connectivity
# (test via actual search request)
```

### Logs Monitoring
Monitor for:
- GitHub API rate limits
- Claude API usage and costs
- Database connection issues
- Learning document creation success

### Learning System Maintenance
- Review generated learning documents weekly
- Consolidate similar patterns monthly
- Archive outdated patterns quarterly
- Update context package optimization

## Security Considerations

### API Keys
- Store in environment variables, never in code
- Use secret management services in production
- Rotate keys regularly
- Monitor usage for anomalies

### GitHub Access
- Use minimal required permissions
- Consider using GitHub App instead of personal token
- Monitor repository changes
- Set up branch protection rules

### Database Security
- Use connection encryption
- Implement read-only database user for searches
- Monitor query execution
- Set up database backups

## Troubleshooting

### Common Issues

#### "GitHub API rate limit exceeded"
- Solution: Wait for rate limit reset or use authenticated requests
- Prevention: Implement request caching

#### "Claude API timeout"
- Solution: Reduce context size or increase timeout
- Prevention: Optimize context package size

#### "Database connection failed"
- Solution: Check database availability and credentials
- Prevention: Implement connection pooling and retries

#### "Learning documents not being created"
- Solution: Check GitHub token permissions and repository access
- Prevention: Monitor GitHub API responses

### Debug Mode
Enable detailed logging:
```bash
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
python claude_github_search_system.py
```

## Cost Optimization

### Claude API Usage
- Monitor token usage via Anthropic console
- Optimize context size to reduce costs
- Implement caching for similar queries
- Set usage alerts

### GitHub API Limits
- Cache repository contents locally
- Use conditional requests with ETags
- Implement intelligent context updates
- Monitor rate limit headers

### Cloud Infrastructure
- Use auto-scaling for variable load
- Implement request caching
- Optimize cold start times
- Monitor resource usage

## Performance Optimization

### Context Package Size
- Limit number of files included
- Compress large text files
- Use incremental updates
- Cache frequently accessed content

### Database Queries
- Add indexes for common search patterns
- Implement query result caching
- Use connection pooling
- Monitor slow queries

### API Response Times
- Implement response caching
- Use CDN for static content
- Optimize JSON serialization
- Monitor response times