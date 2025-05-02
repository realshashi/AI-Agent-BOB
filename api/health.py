"""
Health check endpoint for Vercel monitoring
"""
import os
import sys
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/_health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "vercel",
        "python_version": sys.version,
        "dependencies_loaded": True
    })

# Required for Vercel
application = app