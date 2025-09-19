#!/usr/bin/env python3
"""
Setup script for the Flow Configuration & Chat Application
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements")
        sys.exit(1)

def setup_environment():
    """Setup environment file"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env.example', 'r') as example:
            content = example.read()
        
        with open('.env', 'w') as env_file:
            env_file.write(content)
        
        print("✓ .env file created")
        print("⚠️  Please edit .env and add your Google API key")
        print("   You can get a key from: https://makersuite.google.com/app/apikey")
    else:
        print("✓ .env file already exists")

def create_data_directory():
    """Create data directory for storing configurations"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✓ Data directory created")
    else:
        print("✓ Data directory already exists")

def main():
    """Main setup function"""
    print("Setting up Flow Configuration & Chat Application...")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    setup_environment()
    create_data_directory()
    
    print("\n" + "=" * 50)
    print("Setup complete! 🎉")
    print("\nNext steps:")
    print("1. Edit .env and add your Google API key")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")

if __name__ == "__main__":
    main()