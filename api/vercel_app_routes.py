"""
Frontend route handlers for Vercel deployment
"""
import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from bob_chat import chat_with_bob
from recommendation_engine import analyze_preferences, generate_recommendations
from baxus_api import get_user_bar_data

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = os.environ.get("SECRET_KEY", "bob-whisky-expert-secret")

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat page"""
    return render_template('chat.html', 
                         username=session.get('username'))

@app.route('/recommendations')
def recommendations():
    """Recommendations page"""
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    
    try:
        user_data = get_user_bar_data(username)
        if not user_data:
            flash('No data found for this username', 'warning')
            return redirect(url_for('index'))
        
        preferences = analyze_preferences(user_data)
        recommendations = generate_recommendations(preferences, user_data)
        
        return render_template('recommendations.html',
                             username=username,
                             preferences=preferences,
                             recommendations=recommendations)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error"), 500