# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sserf is a comprehensive automation system for C.S. Lewis live streaming content creation. It combines OBS Studio automation, AI-powered thumbnail generation, and YouTube caption scraping for educational content production.

**Core Purpose**: Automate production tasks for live streams analyzing C.S. Lewis works, allowing the host to focus on content while the system handles scene switching, thumbnail generation, and research assistance.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Linux)
sudo apt install tesseract-ocr portaudio19-dev

# Configure OBS WebSocket (port 4455, set password in .env)
# Enable Tools > WebSocket Server Settings in OBS Studio
```

### Running the System
```bash
# Main automation system (requires OBS Studio running)
python main.py

# Generate thumbnails interactively
python thumbnail_cli.py --interactive

# Generate thumbnail from content
python thumbnail_cli.py --text "Lewis content" --year 1943

# YouTube caption scraping
python youtube_cli.py video "https://youtube.com/watch?v=VIDEO_ID"
python youtube_cli.py channel "https://youtube.com/@channelname"
python youtube_cli.py search "topic"

# Direct caption extraction
python extract_video.py "VIDEO_URL" "output.txt"

# Web search interface for caption database
python web_search.py
```

### Testing
```bash
# Test OBS connection
python examples/test_obs_connection.py

# Test thumbnail generation
python examples/generate_thumbnail.py

# Test YouTube scraping
python examples/test_youtube_scraping.py

# System integration test
python test_system.py
```

## Architecture Overview

### Core Components Structure

**Main Application Flow** (`main.py`):
- `SserfApp` orchestrates all subsystems
- Initializes OBS connection, voice detection, scene management
- Handles graceful shutdown and error recovery
- Provides unified interface for thumbnail generation

**OBS Integration** (`src/obs/`):
- `client.py`: obsws-python wrapper for WebSocket communication
- `scene_manager.py`: High-level scene switching and avatar state management
- Manages "Robot Lady Talking/Idle", "Host Only", "Both Visible" scenes

**Voice Detection** (`src/audio/`):
- `detector.py`: PyAudio-based speaker identification
- Differentiates between host and AI cohost (Robot Lady) speech
- Triggers automatic scene transitions

**Thumbnail Generation** (`src/thumbnail/`):
- `generator.py`: PIL-based thumbnail creation matching series template
- `content_analyzer.py`: AI-powered title generation from content
- Supports text input, OCR from book pages, and manual titles

**YouTube Scraping** (`src/youtube/`):
- `scraper.py`: yt-dlp integration for caption extraction
- Handles single videos, entire channels, and VTT parsing
- Integrates with database for searchable content storage

**Database Layer** (`src/database/`):
- `models.py`: SQLite with FTS5 full-text search for captions
- Video metadata storage and caption segment management
- Export functionality for research and analysis

**Web Search Interface** (`web_search.py`):
- Flask-based web UI for searching caption database
- Real-time search with pagination through 500k+ caption segments
- Direct YouTube links with timestamps for found content
- Video detail pages showing all captions with in-page search

### Configuration System
- Pydantic-based settings in `src/config/settings.py`
- Environment variable configuration via `.env`
- Separate settings classes for OBS, Audio, Thumbnail, and App configs

### Key Integration Points

**Voice-Triggered Scene Management**:
1. Audio detector identifies speaker (host vs Robot Lady)
2. Scene manager switches OBS scenes automatically
3. Avatar states update based on speech detection

**Content-Driven Thumbnail Generation**:
1. Content analyzer processes Lewis text using AI APIs
2. Generates contextual titles (e.g., "Lewis Enjoys Breakfast Literature")
3. Thumbnail generator creates visual matching series template

**Research Workflow Integration**:
1. YouTube scraper builds searchable database of Lewis-related content
2. Caption search enables research across multiple videos
3. Content feeds into thumbnail generation for episode planning

## Development Patterns

### Error Handling Strategy
- Graceful degradation when components fail (e.g., voice detection)
- Comprehensive logging with rotation
- Connection retry logic for OBS WebSocket
- Fallback fonts and templates for thumbnail generation

### Async Architecture
- Main loop uses asyncio for concurrent operations
- OBS WebSocket client supports both sync and async patterns
- Voice detection runs in background with event callbacks
- Scene management responds to real-time audio events

### API Integration
- OpenAI/Anthropic APIs for content analysis (optional)
- yt-dlp for YouTube data extraction
- OBS WebSocket 5.0 protocol for real-time control
- Tesseract OCR for book page text extraction

### Configuration Management
- Environment-based configuration with sensible defaults
- Modular settings allowing component-specific customization
- Runtime configuration validation using Pydantic
- Support for development vs production configurations

## Key Dependencies

**Core Libraries**:
- `obsws-python==1.7.2`: OBS WebSocket client
- `yt-dlp==2023.12.30`: YouTube caption extraction
- `pillow==10.0.0`: Image processing for thumbnails
- `pyaudio==0.2.11`: Real-time audio processing
- `pytesseract==0.3.10`: OCR for book page analysis

**AI Integration** (optional):
- `openai==1.3.0`: Content analysis and title generation
- `anthropic==0.7.0`: Alternative AI provider

**Data Management**:
- SQLite with FTS5: Full-text search for captions
- `pydantic==2.3.0`: Configuration validation

## Thumbnail Text Extraction Protocol

**CRITICAL:** All new videos added to this project must follow the 4-criteria thumbnail text extraction protocol documented in `THUMBNAIL_TEXT_EXTRACTION_PROTOCOL.md`. This ensures accurate search functionality through precise vision-based text extraction.

### The Four Criteria (Apply to ALL new videos):
1. ✅ Individual Claude vision reading (no shortcuts)
2. ✅ Updated thumbnail_text field with exact extracted text
3. ✅ Permanently saved to database  
4. ✅ Committed to GitHub repository

Execute this protocol immediately after caption extraction for any new video to maintain database integrity and search accuracy.

## Critical Implementation Notes

### OBS WebSocket Integration
- Requires OBS Studio 28+ with built-in WebSocket server
- Default port 4455, password configured in `.env`
- Scene names must match expected patterns for automation
- Event subscription for real-time scene change detection

### Voice Detection Calibration
- Requires microphone permissions and proper audio setup
- Threshold adjustment may be needed per environment
- Supports speaker calibration for improved accuracy
- Fallback to manual control if audio detection fails

### Thumbnail Template System
- Matches existing C.S. Lewis series visual design
- Font fallback system for cross-platform compatibility
- Asset directory structure critical for template loading
- Year detection and contextual title generation

### YouTube Scraping Compliance
- Respects rate limiting and YouTube Terms of Service
- Handles private/deleted videos gracefully
- VTT caption parsing with timestamp preservation
- Channel scraping supports various URL formats

## AI Prompting Integration

This project includes a comprehensive AI prompting guide (`COMPREHENSIVE_AI_PROMPTING_GUIDE.md`) that should be referenced when:
- Implementing new AI-powered features
- Optimizing content analysis prompts
- Creating systematic prompt development workflows
- Applying professional prompt engineering techniques

The guide covers the PDER process (Plan, Draft, Evaluate, Refine) and RTSCEN framework for production-grade AI integration.