"""
Serverless entry point for Vercel
This is a lightweight WSGI handler for Vercel's serverless environment
"""
import os
import sys
import logging
from flask import Flask, jsonify

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set Vercel environment flag
os.environ['VERCEL'] = '1'

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fallback app in case the main app fails to load
fallback_app = Flask(__name__)

@fallback_app.route('/')
def index():
    return jsonify({"status": "error", "message": "Failed to load the main application"})

# Try to import the main app
try:
    # Import our Flask app
    from app import app
    logger.info("Successfully imported Flask app in Vercel serverless environment")
    application = app
except Exception as e:
    logger.error(f"Error importing app: {str(e)}")
    # Use fallback app if main app fails to load
    application = fallback_app

# This is required for Vercel's Python runtime
app = application