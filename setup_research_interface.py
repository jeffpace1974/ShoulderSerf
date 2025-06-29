#!/usr/bin/env python3
"""
Setup script for the Captions Database Research Interface
"""

import os
import sys
from pathlib import Path

def setup_anthropic_key():
    """Help user set up Anthropic API key"""
    print("🔍 Captions Database Research Interface Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found. Please make sure you're in the project root directory.")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    if "ANTHROPIC_API_KEY=" in content and "ANTHROPIC_API_KEY=sk-" in content:
        print("✅ Anthropic API key already configured!")
        return True
    
    print("\n📝 To enable AI research capabilities, you need an Anthropic API key.")
    print("\nSteps to get your API key:")
    print("1. Go to https://console.anthropic.com/")
    print("2. Sign up or log in to your account") 
    print("3. Navigate to 'API Keys' section")
    print("4. Create a new API key")
    print("5. Copy the key (starts with 'sk-ant-')")
    
    print("\n🔑 Enter your Anthropic API key (or press Enter to skip):")
    api_key = input().strip()
    
    if not api_key:
        print("⚠️  Skipping API key setup. AI functionality will be limited.")
        return False
    
    if not api_key.startswith('sk-ant-'):
        print("⚠️  Warning: API key doesn't look like a valid Anthropic key (should start with 'sk-ant-')")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Update .env file
    updated_content = content.replace(
        "ANTHROPIC_API_KEY=",
        f"ANTHROPIC_API_KEY={api_key}"
    )
    
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ API key saved to .env file!")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔧 Checking dependencies...")
    
    required_packages = [
        'flask',
        'anthropic',
        'sqlite3'  # This is built-in
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if package == 'sqlite3':
            continue  # Built-in module
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_server():
    """Start the research interface server"""
    print("\n🚀 Starting Captions Database Research Interface...")
    print("   Server will be available at: http://localhost:5003")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    os.system("python3 captions_research_chat.py")

def main():
    print("🎯 Welcome to the Captions Database Research Interface Setup!")
    print("\nThis interface provides advanced AI-powered research capabilities")
    print("for deep analysis of your C.S. Lewis captions database.\n")
    
    # Check if we're in the right directory
    if not Path("captions.db").exists():
        print("❌ captions.db not found in current directory.")
        print("   Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and run setup again.")
        sys.exit(1)
    
    # Setup API key
    api_configured = setup_anthropic_key()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    
    if api_configured:
        print("✅ Full AI research capabilities enabled")
    else:
        print("⚠️  Limited functionality (no AI integration)")
        print("   You can still use the interface for basic database searches")
    
    print("\n📖 Usage Tips:")
    print("• Ask complex research questions about Lewis content")
    print("• Request specific episodes, quotes, and timestamps") 
    print("• Ask for cross-episode analysis and thematic research")
    print("• Get YouTube links with exact timestamps")
    
    start_choice = input("\n🚀 Start the research interface now? (Y/n): ").strip().lower()
    if start_choice != 'n':
        start_server()
    else:
        print("\n💡 To start later, run: python3 captions_research_chat.py")
        print("   Then visit: http://localhost:5003")

if __name__ == "__main__":
    main()