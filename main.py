import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Flask app after loading environment variables
from app import app

# This is for Vercel serverless deployment
# The app object is needed by Vercel
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
