import sys
import os

# Add project root to path so app.py, config.py, skills.py are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel looks for a callable named 'app'
# Flask app object is already named 'app' — nothing else needed
