#!/usr/bin/env python3
"""
AI Sakhi - Application Runner
Simple script to run the AI Sakhi Flask application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🌸 Starting AI Sakhi - Voice-First Health Companion 🌸")
    print("👩‍👧 Your trusted health companion for women and girls")
    print("🎤 Voice-first design with multi-language support")
    print("=" * 60)
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    try:
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n👋 AI Sakhi application stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting AI Sakhi: {e}")
        sys.exit(1)