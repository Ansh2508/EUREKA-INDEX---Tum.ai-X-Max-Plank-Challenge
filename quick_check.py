#!/usr/bin/env python3
"""
Quick check before committing - minimal validation for hackathon development.
"""

def main():
    print("🚀 Quick validation check...")
    
    try:
        # Basic import test
        import main_simple
        print("✅ main_simple.py imports successfully")
        
        # Check if we can create the app
        app = main_simple.app
        print("✅ FastAPI app created successfully")
        
        print("🎉 All basic checks passed! Ready to commit.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("⚠️ Please fix issues before committing.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
