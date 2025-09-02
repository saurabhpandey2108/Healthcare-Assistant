#!/usr/bin/env python3
"""
SAFESPACE AI AGENT - Main Launcher
Unified entry point for all application components
"""

import sys
import subprocess
import os
from pathlib import Path

def run_api():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend...")
    try:
        subprocess.run([
            "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting FastAPI: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("uvicorn not found. Please install it with: uv add uvicorn")
        sys.exit(1)

def run_gradio():
    """Start the Gradio interface"""
    print("Starting Gradio interface...")
    try:
        from views.gradio_ui import safespace_ui
        safespace_ui.launch(
            share=False,
            debug=True,
            server_port=7860
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed with: uv add gradio")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Gradio: {e}")
        sys.exit(1)

def run_streamlit():
    """Start the Streamlit interface"""
    print("Starting Streamlit interface...")
    try:
        subprocess.run([
            "streamlit", 
            "run", 
            "frontend/streamlit_app.py", 
            "--server.port", "8501"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("streamlit not found. Please install it with: uv add streamlit")
        sys.exit(1)

def run_all():
    """Start all services (API + Gradio + Streamlit)"""
    print("🚀 Starting all services...")
    print("Note: This will start services sequentially. Use separate terminals for parallel execution.")
    
    # Start API in background
    print("\n1. Starting FastAPI backend...")
    api_process = subprocess.Popen([
        "uvicorn", 
        "backend.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])
    
    print("\n2. Starting Gradio interface...")
    try:
        from views.gradio_ui import safespace_ui
        safespace_ui.launch(
            share=False,
            debug=True,
            server_port=7860
        )
    except Exception as e:
        print(f"❌ Error starting Gradio: {e}")
        api_process.terminate()
        sys.exit(1)

def show_help():
    """Display help information"""
    help_text = """
🔹 SAFESPACE AI AGENT - Main Launcher 🔹

Usage: python main.py [COMMAND]

Commands:
  api        Start FastAPI backend server (port 8000)
  gradio     Start Gradio interface (port 7860)
  streamlit  Start Streamlit interface (port 8501)
  all        Start API backend + Gradio interface
  help       Show this help message

Examples:
  python main.py api        # Start only the backend API
  python main.py gradio     # Start only Gradio UI
  python main.py streamlit  # Start only Streamlit UI
  python main.py all        # Start API + Gradio

For parallel execution, use separate terminals:
  Terminal 1: python main.py api
  Terminal 2: python main.py gradio
  Terminal 3: python main.py streamlit

Project Structure:
  - Backend API: http://localhost:8000
  - Gradio UI: http://localhost:7860
  - Streamlit UI: http://localhost:8501
  - API Docs: http://localhost:8000/docs
"""
    print(help_text)

def main():
    """Main entry point"""
    print("🤖 SAFESPACE AI AGENT - Mental Health Assistant")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("Expected structure: backend/, frontend/, models/, etc.")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("❌ No command provided.")
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "api":
        run_api()
    elif command == "gradio":
        run_gradio()
    elif command == "streamlit":
        run_streamlit()
    elif command == "all":
        run_all()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
