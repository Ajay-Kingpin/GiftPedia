#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script for Manual Testing
Configures environment and starts servers for manual testing
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_step(step, message):
    """Print a formatted step message"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print('='*60)

def check_requirements():
    """Check if required software is installed"""
    print_step(1, "Checking Requirements")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, '--version'], text=True)
        print(f"✅ Python: {python_version.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(['node', '--version'], text=True)
        print(f"✅ Node.js: {node_version.strip()}")
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        npm_version = subprocess.check_output(['npm', '--version'], text=True)
        print(f"✅ npm: {npm_version.strip()}")
    except:
        print("❌ npm not found")
        return False
    
    return True

def setup_backend():
    """Setup backend environment"""
    print_step(2, "Setting Up Backend")
    
    api_dir = Path("api")
    
    # Create .env file if it doesn't exist
    env_file = api_dir / ".env"
    env_example = api_dir / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating backend .env file from template...")
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Backend .env file created")
            print("⚠️  Please edit api/.env with your actual API keys")
        else:
            print("❌ No .env.example file found")
    else:
        print("✅ Backend .env file already exists")
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      cwd=api_dir, check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    return True

def setup_frontend():
    """Setup frontend environment"""
    print_step(3, "Setting Up Frontend")
    
    frontend_dir = Path("frontend")
    
    # Create .env.local file if it doesn't exist
    env_file = frontend_dir / ".env.local"
    env_example = frontend_dir / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating frontend .env.local file from template...")
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Frontend .env.local file created")
        else:
            print("❌ No .env.example file found")
    else:
        print("✅ Frontend .env.local file already exists")
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    try:
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print("✅ Node.js dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    return True

def start_servers():
    """Start both servers"""
    print_step(4, "Starting Servers")
    
    print("🚀 Starting FastAPI server (http://localhost:8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, 'main.py'],
        cwd=Path("api"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    print("🚀 Starting Next.js server (http://localhost:3000)...")
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=Path("frontend"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("\n🎉 Servers are starting up!")
    print("📍 Frontend: http://localhost:3000")
    print("📍 Backend API: http://localhost:8000")
    print("📍 Health Check: http://localhost:8000/health")
    
    print("\n⚠️  Important Notes:")
    print("   • Make sure you have set your API keys in api/.env")
    print("   • The servers will run in this terminal")
    print("   • Press Ctrl+C to stop both servers")
    
    try:
        # Monitor both processes
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend server stopped")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")

def main():
    """Main setup function"""
    print("🎯 GiftPedia Manual Testing Setup")
    print("This script will configure and start the application for manual testing")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install the required software first")
        return 1
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        return 1
    
    # Start servers
    start_servers()
    
    return 0

if __name__ == "__main__":
    exit(main())
