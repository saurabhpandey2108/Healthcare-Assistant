#!/usr/bin/env python3
"""
SAFESPACE AI AGENT - Service Launcher

This script starts both FastAPI backend and Streamlit frontend together
with proper error handling and dependency checking.
"""

import subprocess
import threading
import time
import sys
import os
from pathlib import Path
import signal
import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ServiceManager:
    """Manages both FastAPI and Streamlit services"""
    
    def __init__(self):
        self.fastapi_process = None
        self.streamlit_process = None
        self.running = True
        
    def start_fastapi(self):
        """Start FastAPI backend server"""
        print("🚀 Starting FastAPI Backend Server...")
        try:
            # Start FastAPI using uvicorn directly
            self.fastapi_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "backend.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ], cwd=str(Path(__file__).parent))
            
            print("✅ FastAPI Backend started on http://localhost:8000")
            return True
        except Exception as e:
            print(f"❌ Failed to start FastAPI: {e}")
            return False
    
    def start_streamlit(self):
        """Start Streamlit frontend"""
        print("🎨 Starting Streamlit Frontend...")
        try:
            # Start Streamlit
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "frontend/streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ], cwd=str(Path(__file__).parent))
            
            print("✅ Streamlit Frontend started on http://localhost:8501")
            return True
        except Exception as e:
            print(f"❌ Failed to start Streamlit: {e}")
            return False
    
    def start_gradio_option(self):
        """Alternative: Start Gradio UI"""
        print("🌐 Alternative: Starting Gradio Interface...")
        try:
            self.gradio_process = subprocess.Popen([
                sys.executable, "main.py", "gradio"
            ], cwd=str(Path(__file__).parent))
            
            print("✅ Gradio Interface started on http://localhost:7860")
            return True
        except Exception as e:
            print(f"❌ Failed to start Gradio: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to start...")
        time.sleep(5)
        
        # Check FastAPI
        try:
            import requests
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI is ready at http://localhost:8000")
            else:
                print("⚠️  FastAPI may not be fully ready")
        except:
            print("⚠️  FastAPI connection test failed")
        
        # Check Streamlit
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("✅ Streamlit is ready at http://localhost:8501")
            else:
                print("⚠️  Streamlit may not be fully ready")
        except:
            print("⚠️  Streamlit connection test failed")
    
    def stop_services(self):
        """Stop all services"""
        print("🛑 Stopping services...")
        self.running = False
        
        if self.fastapi_process:
            self.fastapi_process.terminate()
            print("✅ FastAPI stopped")
        
        if self.streamlit_process:
            self.streamlit_process.terminate()
            print("✅ Streamlit stopped")
    
    def monitor_services(self):
        """Monitor services and restart if needed"""
        while self.running:
            time.sleep(10)
            
            # Check if processes are still running
            if self.fastapi_process and self.fastapi_process.poll() is not None:
                print("⚠️  FastAPI process died, restarting...")
                self.start_fastapi()
            
            if self.streamlit_process and self.streamlit_process.poll() is not None:
                print("⚠️  Streamlit process died, restarting...")
                self.start_streamlit()


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal, stopping services...")
    if 'manager' in globals():
        manager.stop_services()
    sys.exit(0)


def check_dependencies():
    """Check if required dependencies are installed"""
    required = ['fastapi', 'uvicorn', 'streamlit']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("📦 Install them with: pip install fastapi uvicorn streamlit")
        return False
    
    return True


def main():
    """Main entry point"""
    print("🌟 SAFESPACE AI AGENT - Service Manager")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create service manager
    global manager
    manager = ServiceManager()
    
    print("\n🚀 Starting all services...")
    
    # Start services
    fastapi_ok = manager.start_fastapi()
    time.sleep(3)  # Give FastAPI time to start
    
    streamlit_ok = manager.start_streamlit()
    
    if fastapi_ok and streamlit_ok:
        print("\n✅ All services started successfully!")
        print("📍 FastAPI Backend: http://localhost:8000")
        print("📍 Streamlit Frontend: http://localhost:8501")
        print("📚 API Documentation: http://localhost:8000/docs")
        
        # Wait for services to be ready
        manager.wait_for_services()
        
        print("\n🎯 Services are ready! You can now:")
        print("1. Access the Streamlit interface at http://localhost:8501")
        print("2. Test the API at http://localhost:8000/docs")
        print("3. Press Ctrl+C to stop all services")
        
        # Monitor services
        try:
            manager.monitor_services()
        except KeyboardInterrupt:
            pass
    else:
        print("❌ Failed to start some services")
        manager.stop_services()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)