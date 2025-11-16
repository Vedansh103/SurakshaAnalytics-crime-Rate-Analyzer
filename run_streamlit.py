#!/usr/bin/env python3
"""
Simple script to run the Streamlit app
Usage: python run_streamlit.py
"""

import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit application"""
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("🚀 Starting Suraksha Analytics Streamlit App...")
        print("📍 Navigate to the URL shown below in your browser")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped.")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    run_streamlit()