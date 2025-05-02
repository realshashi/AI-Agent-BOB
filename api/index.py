"""
Main entry point for Vercel deployment
Integrates both API and frontend routes
"""
import os
import sys
import logging
import traceback
from flask import Flask, jsonify, request, render_template
from api.middleware import apply_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
logger.info(f"Added parent directory to path: {parent_dir}")

# Initialize Flask app
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')
app.secret_key = os.environ.get("SECRET_KEY", "bob-whisky-expert-secret")

# Apply middleware
apply_middleware(app)

# Import route handlers
try:
    from api.vercel_app_routes import app as frontend_app
    from api.static import app as static_app
    ROUTES_LOADED = True
except Exception as e:
    logger.error(f"Error importing route handlers: {str(e)}")
    logger.error(traceback.format_exc())
    ROUTES_LOADED = False

# Register frontend routes
if ROUTES_LOADED:
    app.register_blueprint(frontend_app)
    app.register_blueprint(static_app, url_prefix='/static')

# API Routes
@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint"""
    if not ROUTES_LOADED:
        return jsonify({"error": "Service unavailable"}), 503
    
    try:
        from bob_chat import chat_with_bob, get_rule_based_response
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message"}), 400
        
        # Check OpenAI API key
        if not os.environ.get("OPENAI_API_KEY"):
            return jsonify({
                "response": "Service unavailable - API key missing",
                "error": "api_key_missing"
            }), 503
        
        # Try rule-based response first
        rule_response = get_rule_based_response(data['message'])
        if rule_response:
            return jsonify({"response": rule_response})
        
        # Use chat function
        response = chat_with_bob(data['message'])
        return jsonify({"response": response})
        
    except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def recommendations_api():
    """Recommendations API endpoint"""
    if not ROUTES_LOADED:
        return jsonify({"error": "Service unavailable"}), 503
    
    try:
        from recommendation_engine import analyze_preferences, generate_recommendations
        from baxus_api import get_user_bar_data
        
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Username required"}), 400
        
        user_data = get_user_bar_data(username)
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        preferences = analyze_preferences(user_data)
        recommendations = generate_recommendations(preferences, user_data)
        
        return jsonify({
            "username": username,
            "preferences": preferences,
            "recommendations": recommendations
        })
        
    except Exception as e:
        logger.exception("Error in recommendations endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def status():
    """Status endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Bob the Whisky Expert API",
        "version": "1.0.0",
        "routes_loaded": ROUTES_LOADED,
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY"))
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Bob the Whisky Expert API",
        "version": "1.0.0",
        "endpoints": {
            "/api/chat": "Chat with Bob (POST)",
            "/api/recommendations": "Get whisky recommendations (GET)",
            "/api/status": "Service status (GET)"
        }
    })

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not found"}), 404
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('error.html', error="Server error"), 500

# This is required for Vercel's Python runtime
application = app