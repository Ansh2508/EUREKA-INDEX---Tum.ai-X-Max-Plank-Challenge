#!/usr/bin/env python3
"""
Simple test runner for local development.
Run this before committing to catch issues early.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and report results."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("STDERR:", result.stderr.strip())
            if result.stdout:
                print("STDOUT:", result.stdout.strip())
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run all local tests."""
    print("🚀 Running local tests before commit...")
    
    tests = [
        ("python -m py_compile main_simple.py", "Syntax check"),
        ('python -c "import main_simple; print(\\"Main app imports OK\\")"', "Import test"),
        ('python -c "from src.analysis import analyze_research_potential; print(\\"Analysis module imports OK\\")"', "Analysis import test"),
    ]
    
    # Only run pytest if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, check=True)
        tests.append(("python -m pytest tests/ -v", "Unit tests"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  pytest not available, skipping unit tests")
    
    passed = 0
    total = len(tests)
    
    for command, description in tests:
        if run_command(command, description):
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to commit.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
