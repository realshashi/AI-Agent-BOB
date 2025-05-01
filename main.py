import os
import logging
from dotenv import load_dotenv

# Set up logging for Vercel environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Load environment variables from .env file (for local development)
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {str(e)}")

# Check for Vercel environment
if os.environ.get('VERCEL') == '1':
    logger.info("Running in Vercel serverless environment")

# Import Flask app after loading environment variables
try:
    from app import app
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask app: {str(e)}")
    raise

# This is for Vercel serverless deployment
# The app object is needed by Vercel
application = app

# Add a health check route
@app.route('/_health')
def health_check():
    return {"status": "ok", "env": "vercel" if os.environ.get('VERCEL') == '1' else "local"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
