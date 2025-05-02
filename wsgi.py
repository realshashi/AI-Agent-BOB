"""
WSGI configuration for Vercel deployment
"""
from api.index import app

# This is required for WSGI servers
application = app

if __name__ == '__main__':
    app.run()