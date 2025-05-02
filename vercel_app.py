"""
Simplified standalone app for Vercel
This creates a minimalistic version of our app with no external dependencies
"""
import os
import sys
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from bob_chat import chat_with_bob
from recommendation_engine import analyze_preferences, generate_recommendations
from baxus_api import get_user_bar_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.environ.get("SESSION_SECRET", "bob-whisky-expert-secret"))

# Static file handling
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message"}), 400
        
        try:
            response = chat_with_bob(data['message'])
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('chat.html')

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    try:
        username = request.args.get('username')
        if not username:
            return render_template('index.html')
        
        user_data = get_user_bar_data(username)
        if not user_data:
            return render_template('index.html', error="No data found for username")
        
        preferences = analyze_preferences(user_data)
        recommendations = generate_recommendations(preferences, user_data)
        
        return render_template('recommendations.html',
                            username=username,
                            preferences=preferences,
                            recommendations=recommendations)
    except Exception as e:
        return render_template('error.html', error=str(e))

# API endpoints
@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "ok",
        "service": "Bob the Whisky Expert",
        "version": "1.0.0"
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)