"""
Simplified standalone app for Vercel
This creates a minimalistic version of our app with no external dependencies
"""
import os
import sys
import logging
from flask import Flask, render_template, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-vercel")

# Add a /vercel route that shows Vercel deployment information
@app.route('/vercel')
def vercel_info():
    # Gather information about the environment
    env_vars = {k: v for k, v in os.environ.items() if not k.startswith(('AWS', 'PYTHON'))}
    
    # Return a simple page with Vercel deployment info
    return jsonify({
        "status": "ok",
        "message": "Bob the Whisky Expert is running on Vercel",
        "environment": "vercel" if os.environ.get('VERCEL') else "development",
        "config": {
            "python_version": sys.version,
            "working_dir": os.getcwd(),
            "sys_path": sys.path
        },
        "environment_variables": env_vars
    })

# Add a health check endpoint
@app.route('/_health')
def health_check():
    return jsonify({"status": "ok", "environment": "vercel"})

# Add a fallback index route
@app.route('/')
def index():
    return render_template('index.html')

# Add a simple status API endpoint
@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "ok",
        "service": "Bob the Whisky Expert API",
        "build_id": os.environ.get("VERCEL_GIT_COMMIT_SHA", "local")
    })

# API endpoint for minimal chat functionality
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message"}), 400
        
        # Return a fixed response if OpenAI API key is missing
        if not os.environ.get("OPENAI_API_KEY"):
            return jsonify({
                "response": "I'm sorry, but I can't access my knowledge base right now. The API key is missing.",
            })
        
        # In a real implementation, we would call the OpenAI API here
        return jsonify({
            "response": "Hello from Bob! I'm currently in limited functionality mode on Vercel. Please try the full application."
        })
    
    except Exception as e:
        logger.exception(f"Error in chat API: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error"), 500

if __name__ == "__main__":
    # Run the app if executed directly
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)