#!/usr/bin/env python3
"""
Phase 1 Setup Verification Script
Checks if all Phase 1 components are properly installed and configured
"""

import sys
import os
import subprocess
import json

def check_python_version():
    """Check if Python 3.11+ is installed"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python version too old. Need 3.11+, got:", f"{version.major}.{version.minor}")
        return False

def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import pytest
        import google.generativeai as genai
        print("✅ Backend dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found")
        return False
    
    package_json = os.path.join(frontend_dir, "package.json")
    if not os.path.exists(package_json):
        print("❌ package.json not found")
        return False
    
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("❌ node_modules not found - run npm install")
        return False
    
    print("✅ Frontend dependencies installed")
    return True

def check_project_structure():
    """Check if project structure is complete"""
    required_dirs = [
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/utils",
        "frontend/src/types",
        "backend/app",
        "backend/agents",
        "backend/services",
        "backend/database",
        "agents/profile_analyzer",
        "agents/creative_idea",
        "agents/filter_rank",
        "agents/explanation_confidence",
        "database/schemas",
        "tests/unit",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ Project structure complete")
        return True

def check_config_files():
    """Check if configuration files exist"""
    required_files = [
        "frontend/package.json",
        "frontend/tsconfig.json",
        "frontend/next.config.js",
        "frontend/jest.config.js",
        "frontend/.env.example",
        "backend/requirements.txt",
        "backend/.env.example",
        "database/schemas/users.sql",
        "database/schemas/products.sql",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ Configuration files complete")
        return True

def check_backend_imports():
    """Check if backend modules can be imported"""
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from app.main import app
        print("✅ Backend imports working")
        return True
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        return False

def check_frontend_build():
    """Check if frontend can build"""
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🚀 GiftPedia Phase 1 Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Backend Dependencies", check_backend_dependencies),
        ("Frontend Dependencies", check_frontend_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration Files", check_config_files),
        ("Backend Imports", check_backend_imports),
        ("Frontend Build", check_frontend_build),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Phase 1 setup is COMPLETE and ready for development!")
        return 0
    else:
        print("⚠️  Phase 1 setup has issues that need to be resolved")
        return 1

if __name__ == "__main__":
    exit(main())
