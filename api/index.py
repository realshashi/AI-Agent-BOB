"""
Serverless entry point for Vercel
This is a lightweight WSGI handler for Vercel's serverless environment
"""
import os
import sys
import logging
import traceback
from flask import Flask, jsonify

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set Vercel environment flag - this must happen before any imports
os.environ['VERCEL'] = '1'

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
logger.info(f"Added parent directory to path: {parent_dir}")

# Fallback app in case the main app fails to load
fallback_app = Flask(__name__)

@fallback_app.route('/')
def fallback_index():
    return jsonify({
        "status": "error", 
        "message": "Failed to load the main application. See logs for details."
    })

@fallback_app.route('/_debug')
def debug_info():
    """Debugging endpoint for Vercel deployment"""
    return jsonify({
        "environment": dict(os.environ),
        "python_path": sys.path,
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "available_files": os.listdir(parent_dir)
    })

@fallback_app.route('/api/status')
def fallback_status():
    """Status endpoint when main app fails to load"""
    return jsonify({
        "status": "error",
        "service": "Bob the Whisky Expert API - Fallback Mode",
        "error": "Main application failed to load"
    })

# Try to import the main app with robust error handling
try:
    # Import main module first which handles dotenv properly
    import main
    logger.info("Successfully imported main module")
    
    # Get app from main module
    app = main.app
    logger.info("Successfully loaded Flask app from main module")
    
    # Ensure we have the application
    application = app
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    logger.error(traceback.format_exc())
    application = fallback_app
    
except Exception as e:
    logger.error(f"Error loading app: {str(e)}")
    logger.error(traceback.format_exc()) 
    application = fallback_app

# This is required for Vercel's Python runtime
app = application