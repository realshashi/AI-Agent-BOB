import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, session
from baxus_api import get_user_bar_data
from recommendation_engine import analyze_preferences, generate_recommendations

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bob-whisky-expert-secret")

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Internal server error. Please try again later."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
