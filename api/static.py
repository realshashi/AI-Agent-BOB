"""
Static file handler for Vercel deployment
"""
from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(static_dir, path)
    except Exception:
        abort(404)

@app.route('/')
def index():
    return {"error": "Not found"}, 404