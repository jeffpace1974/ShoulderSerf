# Sserf Validation Guide

This guide helps you test and validate your C.S. Lewis streaming automation system.

## 🚀 Quick Start Validation

### Step 1: Basic Functionality Test
```bash
# Run this first - tests core thumbnail generation
python quick_test.py
```

This will:
- ✅ Test basic thumbnail generation
- ✅ Test content analysis without AI
- ✅ Create sample thumbnails
- ✅ Verify core system is working

### Step 2: Full System Test
```bash
# Run comprehensive test of all features
python test_system.py
```

This will test:
- 📦 All dependencies
- 🎨 Thumbnail generation (basic + AI)
- 📷 OCR functionality (if Tesseract installed)
- 📺 OBS WebSocket connection (if OBS running)
- 🎤 Voice detection (if microphone available)
- 💻 CLI interface

## 🎨 Thumbnail Generation Tests

### Test 1: Manual Thumbnail
```bash
python thumbnail_cli.py --text "Lewis discusses his love of bacon and medieval literature during a 1943 Oxford lunch" --year 1943
```

**Expected Result:** Creates a thumbnail with title like "Lewis Discusses Medieval Literature" and year "1943"

### Test 2: Interactive Mode
```bash
python thumbnail_cli.py --interactive
```

**Try these inputs:**
1. **Text content:** "Today Lewis had quite the amusing debate about Tom Jones with his colleague. He argued that Fielding's novel contains genuine moral instruction."
2. **Year:** 1941
3. **Expected title:** Something like "Lewis Defends Tom Jones"

### Test 3: Book Page Image (if you have one)
```bash
python thumbnail_cli.py --image path/to/book_page.jpg --year 1924
```

**Expected Result:** OCR extracts text, AI generates title, creates thumbnail

### Test 4: Content Analysis Only
```bash
python thumbnail_cli.py --text "Lewis writes about his morning bacon and eggs while reading Malory's tales of King Arthur" --analyze-only
```

**Expected Output:**
```
Generated Title: Lewis Enjoys Bacon While Reading Malory
Detected Year: [varies]
Themes: literature, personal
Analysis Method: rule-based (or ai if configured)
```

## 📺 OBS Integration Tests

### Prerequisites
1. **Start OBS Studio**
2. **Enable WebSocket:**
   - Tools > WebSocket Server Settings
   - Check "Enable WebSocket server"
   - Port: 4455
   - Set password (optional)
3. **Update .env file** with OBS password

### Test OBS Connection
```bash
python examples/test_obs_connection.py
```

**Expected Results:**
- ✅ Connection to OBS successful
- ✅ Scene list retrieved
- ✅ Current scene identified
- ✅ Basic operations working

### Test Scene Automation
1. **Create test scenes in OBS:**
   - "Robot Lady Talking"
   - "Robot Lady Idle"
   - "Host Only"
   - "Both Visible"

2. **Run automation test:**
```bash
python main.py
```

3. **Test voice detection** (speak into microphone)
   - Should automatically switch scenes based on speaker

## 🔧 Troubleshooting Common Issues

### "Missing Dependencies" Error
```bash
pip install -r requirements.txt
```

### "Tesseract not found" Error
```bash
# Linux/WSL
sudo apt install tesseract-ocr

# Mac
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### "OBS Connection Failed" Error
1. Check OBS is running
2. Verify WebSocket enabled in OBS settings
3. Check password in .env matches OBS settings
4. Try without password first (leave OBS_PASSWORD empty)

### "PyAudio Error" Error
```bash
# Linux/WSL
sudo apt install portaudio19-dev
pip install pyaudio

# Mac
brew install portaudio
pip install pyaudio
```

### Thumbnail Generation Issues
1. **Font problems:** System will fallback to default fonts
2. **Permission errors:** Check write permissions in thumbnails directory
3. **Template missing:** The system creates fallback backgrounds

## 📋 Validation Checklist

### Core Features
- [ ] Basic thumbnail generation works
- [ ] Content analysis generates reasonable titles
- [ ] CLI interface responds to commands
- [ ] Files are created in thumbnails directory

### Advanced Features
- [ ] OCR extracts text from images
- [ ] AI generates engaging titles (if API keys set)
- [ ] Year detection works from content
- [ ] Template design matches your example

### OBS Integration
- [ ] Connects to OBS WebSocket
- [ ] Can retrieve scene list
- [ ] Can switch scenes programmatically
- [ ] Scene manager initializes properly

### Voice Detection
- [ ] Audio input detected
- [ ] Voice activity recognition working
- [ ] Speaker differentiation attempted
- [ ] Scene switching triggered by voice

## 🎯 Success Criteria

**Minimum Working System:**
- ✅ Basic thumbnail generation
- ✅ CLI interface functional
- ✅ Content analysis working

**Full Featured System:**
- ✅ All above plus OCR support
- ✅ OBS scene automation
- ✅ Voice-triggered scene switching
- ✅ AI-powered title generation

## 🆘 Getting Help

If tests fail:

1. **Check the error messages** in test output
2. **Verify Python version:** `python --version` (need 3.8+)
3. **Check dependencies:** All packages in requirements.txt installed
4. **Review configuration:** .env file properly set up
5. **Test incrementally:** Start with quick_test.py, then build up

**Common Working Configuration:**
- Python 3.8+
- PIL/Pillow for image processing
- Basic font support (system fonts)
- No AI keys needed for basic operation
- OBS optional for streaming features

The system is designed to work incrementally - core thumbnail generation should work immediately, with advanced features enabled as you add dependencies and configuration.