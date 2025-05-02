"""
Middleware for Vercel deployment
"""
from functools import wraps
from flask import request, current_app

def add_cors_headers(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=()'
    return response

def apply_middleware(app):
    """Apply all middleware to Flask app"""
    app.after_request(add_cors_headers)
    app.after_request(add_security_headers)
    
    # Handle OPTIONS requests for CORS
    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            response = current_app.make_default_options_response()
            add_cors_headers(response)
            return response