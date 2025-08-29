#!/usr/bin/env python3
"""
Setup script for Shorts Factory
"""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True


def setup_environment():
    """Setup environment configuration"""
    print("🔧 Setting up environment configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("📋 Copying .env.example to .env")
        env_file.write_text(env_example.read_text())
        print("⚠️  Please edit .env file with your API keys before running the application")
    elif env_file.exists():
        print("ℹ️  .env file already exists")
    else:
        print("❌ No .env.example file found")
        return False
    
    return True


def main():
    """Main setup function"""
    print("🚀 Setting up Shorts Factory...")
    
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    if not setup_environment():
        print("❌ Setup failed during environment configuration")
        sys.exit(1)
    
    print("🎉 Shorts Factory setup complete!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Run: python src/main.py test")
    print("3. Run: python src/main.py run-once")


if __name__ == '__main__':
    main()
