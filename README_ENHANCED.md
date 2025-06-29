# Shoulder Serf - Complete C.S. Lewis Content Creation & Research Suite 🌊

<div align="center">

![Shoulder Serf Logo](assets/SSerf%20Logo.jpg)

**Comprehensive automation system for C.S. Lewis live streaming content creation with enhanced YouTube caption search**

[![GitHub](https://img.shields.io/badge/GitHub-ShoulderSerf-blue)](https://github.com/jeffpace1974/ShoulderSerf)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![OBS](https://img.shields.io/badge/OBS-WebSocket-red)](https://obsproject.com)
[![Flask](https://img.shields.io/badge/Flask-Web%20Interface-lightblue)](https://flask.palletsprojects.com)

</div>

---

## 🎯 Project Overview

Shoulder Serf is a comprehensive automation system designed to enhance live streaming of C.S. Lewis literary analysis sessions. The project combines OBS Studio automation, AI-powered content generation, and advanced YouTube caption research tools.

### 🌟 Core Features

1. **🤖 OBS Studio Automation** - Voice-activated scene switching for Robot Lady avatar states
2. **🎨 AI-Powered Thumbnail Generation** - Create engaging episode thumbnails from content or book page photos  
3. **🔍 Enhanced YouTube Caption Search** - Advanced search system with thumbnails, tags, and playlists
4. **📚 Content Analysis** - Generate engaging titles and extract insights from C.S. Lewis materials
5. **🌐 Web Search Interface** - Beautiful, responsive search portal with AI-powered concept search

---

## 🆕 Latest Enhancements

### ✨ Enhanced Search System
- **Thumbnail OCR**: Extract and search text from video thumbnails
- **Tag Integration**: Search through video tags and metadata
- **Playlist Data**: Organize content by playlists and collections
- **AI Concept Search**: Intelligent query understanding beyond keyword matching
- **Modern UI**: Ocean wave-themed design matching the Shoulder Serf brand

### 🎨 Visual Improvements
- **Custom Branding**: Integrated Shoulder Serf logo and ocean wave theme
- **Responsive Design**: Works beautifully on desktop and mobile
- **Interactive Elements**: Smooth animations and hover effects
- **Professional Styling**: Glass-morphism effects and gradient aesthetics

---

## 🚀 Quick Start

### 📋 Prerequisites
- **OBS Studio** (v28+ with built-in WebSocket server)
- **Python 3.8+** 
- **Tesseract OCR** (for thumbnail text extraction)
- **Audio input device** (microphone for voice detection)
- **Windows/Linux/macOS** (tested on WSL2)

### ⚡ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jeffpace1974/ShoulderSerf.git
   cd ShoulderSerf
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   
   # Install OCR support (Ubuntu/Debian)
   sudo apt update && sudo apt install tesseract-ocr
   
   # Install OCR support (macOS)
   brew install tesseract
   ```

3. **Configure OBS Studio:**
   - Open OBS Studio → **Tools > WebSocket Server Settings**
   - Enable WebSocket server (port 4455)
   - Set password and update `.env` file

4. **Start the search website:**
   ```bash
   # Enhanced version (port 5000)
   python web_search.py
   
   # Development version (port 5001) 
   python web_search_dev.py
   ```

5. **Access your search portal:**
   - **Enhanced**: http://localhost:5000
   - **Development**: http://localhost:5001

---

## 🎬 Main Applications

### 🔍 YouTube Caption Search
**Access the beautiful web interface at http://localhost:5000**

**Features:**
- 🖼️ **Thumbnail Display**: Visual search results with video thumbnails
- 🏷️ **Tag Search**: Find videos by tags and metadata
- 📂 **Playlist Integration**: Organize by playlists and collections
- 🧠 **AI Concept Search**: Ask natural language questions
- ⚡ **Real-time Search**: Instant results as you type
- 📱 **Mobile Responsive**: Works perfectly on any device

### 🎨 Thumbnail Generation
```bash
# Interactive mode (recommended)
python thumbnail_cli.py --interactive

# Generate from text content
python thumbnail_cli.py --text "Lewis discusses medieval literature" --year 1943

# Generate from book page image (OCR)
python thumbnail_cli.py --image book_page.jpg --year 1924
```

### 📺 YouTube Caption Scraping
```bash
# Scrape single video with full metadata
python youtube_cli.py video "https://youtube.com/watch?v=VIDEO_ID"

# Scrape entire channel
python youtube_cli.py channel "https://youtube.com/@channelname"

# Search through captions
python youtube_cli.py search "Narnia creation"

# Extract to text file
python extract_video.py "VIDEO_URL" "output.txt"
```

### 🤖 OBS Automation
```bash
# Start full automation system
python main.py
```

---

## 🌐 Web Search Interface

### 🎯 Search Types

**Keyword Search**: Traditional text matching
```
Example: "microscope" → Finds exact word matches
```

**Concept Search (AI)**: Intelligent understanding
```
Example: "Lewis's scientific interests" → Understands context and intent
```

### 🔧 Search Features

- **📊 Real-time Statistics**: Video count, caption segments, database size
- **🎨 Visual Results**: Thumbnails, tags, playlists displayed beautifully
- **⚡ Fast Pagination**: Navigate through thousands of results
- **🔗 Direct Links**: Jump to YouTube timestamps or view full captions
- **📱 Mobile Optimized**: Perfect experience on any device

### 🎨 Design Features

- **🌊 Ocean Wave Theme**: Matching the Shoulder Serf brand
- **✨ Smooth Animations**: Gentle hover effects and transitions
- **💎 Glass Morphism**: Modern, professional appearance
- **🎯 Intuitive Navigation**: Easy to use for any skill level

---

## 📁 Project Structure

```
ShoulderSerf/
├── 🌊 assets/                     # Logos, templates, images
│   ├── SSerf Logo.jpg            # Main Shoulder Serf logo
│   └── thumbnail_template.png    # Thumbnail generation template
├── 📚 src/                       # Core source code
│   ├── audio/                    # Voice detection & processing
│   ├── automation/               # Scene management & triggers
│   ├── config/                   # Configuration & settings
│   ├── database/                 # Enhanced database with FTS5
│   ├── obs/                      # OBS WebSocket integration
│   ├── search/                   # AI-powered concept search
│   ├── thumbnail/                # OCR extraction & generation
│   └── youtube/                  # Enhanced scraping with metadata
├── 🌐 templates/                 # Web interface templates
│   └── search.html              # Enhanced search interface
├── 📝 docs/                      # Documentation
├── ⚡ examples/                  # Usage examples & demos
├── 🔧 web_search.py             # Enhanced search website (port 5000)
├── 🔧 web_search_dev.py         # Development version (port 5001)
├── 📈 enhance_existing_videos.py # Batch enhancement script
└── 🎯 main.py                   # OBS automation system
```

---

## 🔧 Advanced Usage

### 📊 Enhance Existing Video Database
```bash
# Test enhancement on 5 videos
python enhance_existing_videos.py --limit 5 --dry-run

# Process all videos with metadata extraction
python enhance_existing_videos.py --yes

# Custom batch processing
python enhance_existing_videos.py --limit 50 --batch-size 5 --yes
```

### 🧠 AI Concept Search Examples

**Biographical Questions:**
- "Lewis's relationship with his father"
- "His views on pain and suffering" 
- "Lewis's conversion experience"

**Academic Topics:**
- "His teaching methods at Oxford"
- "Student reactions to his lectures"
- "Medieval literature influences"

**Literary Analysis:**
- "Creation themes in Narnia"
- "Christian allegory in his works"
- "Friendship with Tolkien"

### 🎨 Programmatic Thumbnail Generation
```python
from src.thumbnail.generator import ThumbnailGenerator

generator = ThumbnailGenerator()

# AI-powered title generation
output = generator.generate_from_content(
    "Lewis had quite the debate about Tom Jones today...",
    year="1941"
)

# OCR from book page
output = generator.generate_from_image(
    "book_page.jpg", 
    year="1924"
)
```

---

## ⚙️ Configuration

### 🔐 Environment Variables (`.env`)
```env
# OBS WebSocket Settings
OBS_PASSWORD=your_obs_password
OBS_PORT=4455

# Audio Detection
AUDIO_VOICE_THRESHOLD=0.01

# AI Integration (Optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# File Paths
THUMBNAIL_OUTPUT_DIR=./thumbnails
DATABASE_PATH=./captions.db
```

### 🎛️ OBS Scene Setup
Create these scenes for full automation:
- `Robot Lady Talking` - AI avatar in active state
- `Robot Lady Idle` - AI avatar in idle state  
- `Host Only` - Show only the host
- `Both Visible` - Show both host and AI

---

## 🛠️ Development & Deployment

### 📋 Step-by-Step Deployment Log

**Phase 1: GitHub Repository Setup**
1. Create repository at `https://github.com/jeffpace1974/ShoulderSerf`
2. Set as **Public** for free GitHub Actions and Cloudflare Pages
3. Add description: "Comprehensive automation system for C.S. Lewis live streaming content creation with YouTube caption search"

**Phase 2: Local Git Configuration**
```bash
# Initialize Git
git init

# Configure Git
git config user.name "jeffpace1974"
git config user.email "your-email@example.com"

# Create .gitignore
echo "__pycache__/
*.pyc
.env
venv/
*.log
*.db" > .gitignore

# Initial commit
git add .
git commit -m "Initial commit: Complete Shoulder Serf automation system with enhanced caption search

🌊 Features:
- Enhanced YouTube caption search with thumbnails, tags, playlists
- AI-powered concept search with natural language queries  
- Beautiful ocean wave-themed web interface
- OCR thumbnail text extraction with Tesseract
- OBS Studio automation with voice detection
- Comprehensive C.S. Lewis content creation suite

🎯 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Connect to GitHub
git remote add origin https://github.com/jeffpace1974/ShoulderSerf.git
git branch -M main
git push -u origin main
```

**Phase 3: Cloudflare Pages Setup** *(Next Steps)*
1. Connect Cloudflare to GitHub repository
2. Configure automatic deployments on push
3. Set up custom domain (optional)

---

## 🎯 Use Cases

### 📚 Primary: C.S. Lewis Literary Analysis
- **Content**: Systematic reading through Lewis's complete works
- **Format**: Live YouTube streams with AI cohost discussion  
- **Audience**: Lewis enthusiasts, literature students, scholars
- **Goal**: Deep understanding of Lewis's intellectual development

### 🔬 Research Applications
- **Academic Research**: Search across hundreds of Lewis-related videos
- **Quote Finding**: Locate specific passages or topics instantly
- **Content Planning**: Use search insights for episode planning
- **Audience Engagement**: Answer viewer questions with precise references

### 🎬 Production Workflow
- **Automated OBS**: Focus on content, not technical production
- **Smart Thumbnails**: Generate engaging visuals automatically
- **Research Integration**: Quick access to relevant background material
- **Professional Quality**: Maintain high production standards effortlessly

---

## 🚀 Future Enhancements

- 🌍 **Multi-language Support**: Expand beyond English content
- 📱 **Mobile App**: Companion app for remote control
- 🤖 **Advanced AI**: GPT-4 integration for deeper content analysis
- 📊 **Analytics Dashboard**: Stream performance and engagement metrics
- 🔄 **Auto-Updates**: Cloudflare integration for seamless deployments
- 🎵 **Audio Analysis**: Sentiment and topic detection from speech
- 📖 **Ebook Integration**: Direct quotes and references from Lewis's works

---

## 🤝 Contributing

This project welcomes contributions focusing on:
- 🎯 **OBS Automation**: Enhanced voice detection and scene management
- 🔍 **Search Improvements**: Better AI understanding and result relevance  
- 🎨 **UI/UX Enhancements**: Design improvements and accessibility
- 📚 **Content Integration**: New Lewis-related data sources
- 🐛 **Bug Fixes**: Issue resolution and performance optimization

### 📬 Contact
- **GitHub**: [@jeffpace1974](https://github.com/jeffpace1974)
- **Project**: [ShoulderSerf Repository](https://github.com/jeffpace1974/ShoulderSerf)

---

## 📄 License

[To be determined based on project requirements]

---

<div align="center">

### 🌊 *"The real problem is not why some pious, humble, believing people suffer, but why some do not."* - C.S. Lewis

**Built with ❤️ for the C.S. Lewis community**

*🤖 Enhanced with Claude Code*

</div>