#!/usr/bin/env python3
"""
🚀 Suraksha Analytics Launcher
Simple launcher for the Streamlit web application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'pandas', 'plotly', 'seaborn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    """Main launcher function"""
    print("🚀 SURAKSHA ANALYTICS LAUNCHER")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("streamlit_main.py").exists():
        print("❌ streamlit_main.py not found!")
        print("💡 Make sure you're running this from the project directory")
        return
    
    if not Path("Dataset").exists():
        print("❌ Dataset folder not found!")
        print("💡 Make sure the Dataset folder is in the same directory")
        return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"📋 Missing packages: {', '.join(missing)}")
        if input("Install missing packages? (y/n): ").lower() == 'y':
            if not install_dependencies():
                return
        else:
            print("❌ Cannot run without required packages")
            return
    
    print("✅ All dependencies satisfied!")
    print("🌐 Starting Streamlit application...")
    print("📊 Open your browser to: http://localhost:8501")
    print("💡 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_main.py',
            '--server.port', '8501',
            '--server.headless', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()