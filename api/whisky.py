"""
Simplified API endpoint for Bob the Whisky Expert on Vercel
"""
import os
import sys
import json
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a simple API app
app = Flask(__name__)

try:
    # Import our chat functionality
    from bob_chat import chat_with_bob, add_to_cache, get_rule_based_response
    logger.info("Successfully imported whisky chat modules")
    CHAT_AVAILABLE = True
except Exception as e:
    logger.error(f"Error importing chat modules: {str(e)}")
    CHAT_AVAILABLE = False

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Simple API endpoint for chatting with Bob"""
    if not CHAT_AVAILABLE:
        return jsonify({
            "error": "Chat functionality not available",
            "message": "The chat service is currently unavailable"
        }), 503
    
    try:
        data = request.json
        if not data or not data.get('message'):
            return jsonify({"error": "Missing message"}), 400
        
        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            return jsonify({
                "response": "I apologize, but I'm not available right now. The API key is missing. Please contact the administrator.",
                "error": "api_key_missing"
            }), 503
        
        # Create simple message format
        message = data.get('message')
        username = data.get('username')
        
        # Try rule-based response first
        rule_response = get_rule_based_response(message)
        if rule_response:
            return jsonify({"response": rule_response})
        
        # Use chat function with minimal context
        messages = [{"role": "user", "content": message}]
        response = chat_with_bob(messages, username)
        
        return jsonify({"response": response})
    
    except Exception as e:
        logger.exception(f"Error in chat API: {str(e)}")
        return jsonify({
            "error": "server_error",
            "message": "An error occurred processing your request"
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Status endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Bob the Whisky Expert API",
        "chat_available": CHAT_AVAILABLE,
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY"))
    })

# Default route
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route that forwards to the status endpoint"""
    return jsonify({
        "error": "not_found",
        "message": f"Endpoint '{path}' not found. Use /api/chat for chat functionality."
    }), 404