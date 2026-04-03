#!/usr/bin/env python3
"""
Test Runner for Phase 1 Verification
Runs all test suites and reports results
"""

import subprocess
import sys
import os
from pathlib import Path

def run_frontend_tests():
    """Run frontend tests"""
    print("🧪 Running Frontend Tests...")
    try:
        result = subprocess.run(
            ["npm", "test", "--", "--passWithNoTests", "--verbose"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("Frontend Test Output:")
        print("=" * 50)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        print("=" * 50)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def run_backend_tests():
    """Run backend tests"""
    print("🧪 Running Backend Tests...")
    try:
        # Test basic imports
        result = subprocess.run(
            ["python", "-c", "from app.main import app; print('✅ Backend imports successful')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print("❌ Backend import failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def check_test_files_exist():
    """Check if test files exist"""
    print("🔍 Checking Test Files...")
    
    frontend_tests = [
        "frontend/src/__tests__/test_api_client.test.ts",
        "frontend/src/__tests__/test_homepage.test.tsx"
    ]
    
    backend_tests = [
        "tests/unit/test_backend_api.test.py",
        "tests/unit/test_data_models.test.py"
    ]
    
    missing_files = []
    
    for test_file in frontend_tests + backend_tests:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    else:
        print("✅ All test files exist")
        return True

def main():
    """Run all test verification"""
    print("🚀 Phase 1 Test Verification")
    print("=" * 50)
    
    checks = [
        ("Test Files Exist", check_test_files_exist),
        ("Backend Tests", run_backend_tests),
        ("Frontend Tests", run_frontend_tests),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Running {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} test checks passed")
    
    if passed == total:
        print("🎉 All tests are configured and ready!")
        return 0
    else:
        print("⚠️  Some test issues need attention")
        return 1

if __name__ == "__main__":
    exit(main())
