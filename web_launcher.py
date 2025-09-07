#!/usr/bin/env python3
"""
Web interface launcher for E-commerce Chatbot
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
from threading import Thread

def start_api():
    """Start FastAPI backend"""
    print("Starting FastAPI backend...")
    subprocess.run([sys.executable, "src/interfaces/web_api.py"])

def start_frontend():
    """Start Streamlit frontend"""
    print("Starting Streamlit frontend...")
    time.sleep(2)  # Wait for API to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/interfaces/web_frontend.py"])

def main():
    print("E-commerce Chatbot Web Interface")
    print("=" * 50)
    print("Starting both backend and frontend...")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:8501")
    print("=" * 50)
    
    # Start API in background thread
    api_thread = Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Start frontend (main thread)
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")