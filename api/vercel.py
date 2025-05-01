"""
Dedicated entry point for Vercel with minimal dependencies.
This file contains a streamlined version of our app specifically for Vercel.
"""
import os
import sys
import json
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a basic Flask app for Vercel
app = Flask(__name__)

# Set environment flag for Vercel
os.environ['VERCEL'] = '1'

# Add common responses for whisky questions
COMMON_RESPONSES = {
    "smoky": "For smoky flavors, I'd recommend Islay whiskies like Laphroaig, Ardbeg, or Lagavulin. They're known for their intense peat smoke character.",
    "region": "The main whisky regions in Scotland are: Highlands, Lowlands, Speyside, Islay, and Campbeltown. Each has distinctive characteristics.",
    "new": "To start exploring whisky, try these approachable options: Glenmorangie Original (Highland), Monkey Shoulder (Blended Scotch), Buffalo Trace (Bourbon), or Jameson (Irish).",
    "difference": "The difference between whisky and whiskey is primarily about origin. 'Whisky' (no 'e') is typically used in Scotland, Canada, and Japan. 'Whiskey' (with an 'e') is used in Ireland and the United States.",
    "under 50": "For under $50, I recommend Buffalo Trace or Wild Turkey 101 for bourbon fans, Monkey Shoulder for a smooth blended Scotch, or Jameson Black Barrel for Irish whiskey enthusiasts.",
    "taste": "To properly taste whisky: 1) Look at the color, 2) Nose it gently, 3) Take a small sip and let it coat your mouth, 4) Consider adding a few drops of water to open up flavors, 5) Think about the finish and lingering tastes.",
    "food": "Whisky pairs wonderfully with dark chocolate, aged cheeses like cheddar, smoked salmon, grilled meats, and even desserts like caramel or fruit tarts.",
    "single malt": "A single malt whisky is made from 100% malted barley at one distillery. Unlike blended whiskies, which combine spirits from multiple distilleries.",
    "gift": "For a gift, Macallan 12 is always impressive with its rich sherry character, Balvenie 14 Caribbean Cask offers unique rum-influenced flavors, and Hibiki Harmony presents beautifully with its elegant bottle.",
    "favorite": "While I appreciate many different whiskies, I particularly enjoy Springbank 15 for its complex character combining light smoke, fruit, and maritime notes, all from traditional production methods."
}

@app.route('/api/status')
def status():
    """Status endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Bob the Whisky Expert API (Vercel)",
        "environment": "vercel",
        "version": "1.0.0"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat API endpoint"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message parameter"}), 400
            
        message = data['message'].lower()
        
        # Check for common whisky questions
        for keyword, response in COMMON_RESPONSES.items():
            if keyword in message:
                return jsonify({"response": response})
        
        # If no match, return a fallback response
        return jsonify({
            "response": "I'm Bob, your whisky expert. While I'm running in a limited mode on Vercel, I can help with basic whisky questions. Ask me about smoky whiskies, regions, or recommendations for beginners."
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return jsonify({
            "error": "server_error",
            "message": "An error occurred processing your request"
        }), 500

@app.route('/')
def home():
    """Vercel status page"""
    return jsonify({
        "status": "online",
        "app": "Bob the Whisky Expert",
        "environment": "vercel",
        "apis": ["/api/status", "/api/chat"],
        "message": "This is a serverless API endpoint. Visit the main application for the full experience."
    })

@app.route('/_debug')
def debug():
    """Debugging info"""
    env_list = {k: v for k, v in os.environ.items() 
               if not k.startswith(('AWS', 'PYTHON', 'PATH'))}
    
    return jsonify({
        "env": env_list,
        "python_version": sys.version,
        "path": sys.path
    })

# Required for Vercel
application = app