import os
import logging
import json
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from baxus_api import get_user_bar_data
from recommendation_engine import analyze_preferences, generate_recommendations
from bob_chat import chat_with_bob

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check if OpenAI API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set. Chat functionality will be limited.")

# Check if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'
if IS_VERCEL:
    logger.info("Running on Vercel serverless environment")

# Initialize Flask app
app = Flask(__name__)

# Set secure secret key for sessions
app.secret_key = os.environ.get("SECRET_KEY", os.environ.get("SESSION_SECRET", "bob-whisky-expert-secret"))

# Configure session cookie for Vercel deployment
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Set Flask environment configuration
app.config['DEBUG'] = not IS_VERCEL and os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with username form"""
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash('Please enter a BAXUS username', 'danger')
            return redirect(url_for('index'))
        
        # Store username in session for recommendations page
        session['username'] = username
        return redirect(url_for('recommendations'))
    
    return render_template('index.html')

@app.route('/recommendations')
def recommendations():
    """Recommendations page showing personalized bottle suggestions"""
    username = session.get('username')
    if not username:
        flash('Please enter a BAXUS username first', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Get user's bar data from BAXUS API
        user_data = get_user_bar_data(username)
        
        if not user_data or 'bar' not in user_data or not user_data['bar']:
            flash('No bottle collection found for this username. Please try another username or contact BAXUS support.', 'warning')
            return redirect(url_for('index'))
        
        # Analyze user preferences
        user_preferences = analyze_preferences(user_data)
        
        # Generate recommendations based on preferences
        recommendations = generate_recommendations(user_preferences, user_data)
        
        return render_template('recommendations.html', 
                               username=username, 
                               preferences=user_preferences, 
                               recommendations=recommendations)
    
    except Exception as e:
        logger.exception("Error generating recommendations")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat with Bob the Whisky Expert"""
    username = session.get('username')
    recommendations = []
    user_preferences = None
    
    # If user has logged in, get their preferences and recommendations
    if username:
        try:
            # Get user's bar data from BAXUS API
            user_data = get_user_bar_data(username)
            
            # If user has bottle collection, analyze preferences
            if user_data and 'bar' in user_data and user_data['bar']:
                user_preferences = analyze_preferences(user_data)
                recommendations = generate_recommendations(user_preferences, user_data)
        except Exception as e:
            logger.exception(f"Error loading user data for chat: {str(e)}")
    
    # Handle chat API requests
    if request.method == 'POST' and request.is_json:
        message = request.json.get('message', '')
        
        # Get chat history from session
        chat_history = session.get('chat_history', [])
        
        # Add the new user message to history
        chat_history.append({"role": "user", "content": message})
        
        # Check if OpenAI API key is available
        if not OPENAI_API_KEY:
            api_error_msg = "I'm unable to connect to my whisky knowledge base at the moment. The OpenAI API key is missing or invalid. Please contact the administrator."
            logger.error("Missing OpenAI API key for chat request")
            
            # Add error response to history
            chat_history.append({"role": "assistant", "content": api_error_msg})
            session['chat_history'] = chat_history[-20:] if len(chat_history) > 20 else chat_history
            return jsonify({"response": api_error_msg, "error": "api_key_missing"})
        
        try:
            # Get response from Bob
            bob_response = chat_with_bob(chat_history, username, user_preferences)
            
            # Add Bob's response to history
            chat_history.append({"role": "assistant", "content": bob_response})
            
            # Save updated history to session (limit to last 20 messages to avoid session bloat)
            session['chat_history'] = chat_history[-20:] if len(chat_history) > 20 else chat_history
            
            # Return the response
            return jsonify({"response": bob_response})
            
        except Exception as e:
            error_msg = "I apologize, but I'm experiencing technical difficulties. Please try again shortly."
            
            # Check for specific OpenAI errors
            error_str = str(e).lower()
            if "rate limit" in error_str or "quota" in error_str:
                error_msg = "I apologize, but I've reached my connection limit to the whisky knowledge base. Please try again later or contact the administrator."
            
            logger.exception(f"Error in chat: {str(e)}")
            
            # Add error response to history
            chat_history.append({"role": "assistant", "content": error_msg})
            session['chat_history'] = chat_history[-20:] if len(chat_history) > 20 else chat_history
            
            return jsonify({"response": error_msg, "error": "api_error"})
    
    # For GET requests, render the chat page
    return render_template('chat.html', 
                           username=username, 
                           recommendations=recommendations)

@app.route('/chat/reset', methods=['POST'])
def reset_chat():
    """Reset the chat history"""
    session.pop('chat_history', None)
    return jsonify({"success": True})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Internal server error. Please try again later."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
