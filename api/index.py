import sys
import os

# Add the 'backend' folder to sys.path so 'from app import ...' works inside main.py
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.main import app
