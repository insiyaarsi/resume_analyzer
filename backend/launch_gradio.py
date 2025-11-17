"""
Launch script for Gradio interface.
Ensures proper Python path setup.
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import and run the Gradio app
from app.gradio_app import main

if __name__ == "__main__":
    print("="*60)
    print("ResumeForge - Gradio Interface")
    print("="*60)
    print("\nInitializing models and services...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the backend folder")
        print("2. Virtual environment is activated")
        print("3. All dependencies are installed")