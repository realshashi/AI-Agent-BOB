import os
import logging

# Set up logging for Vercel environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for Vercel environment
is_vercel = os.environ.get('VERCEL') == '1'
if is_vercel:
    logger.info("Running in Vercel serverless environment")
else:
    # Only load dotenv in non-Vercel environments
    try:
        # Try to import dotenv for local development
        from dotenv import load_dotenv
        # Load environment variables from .env file
        load_dotenv()
        logger.info("Environment variables loaded from .env file")
    except ImportError:
        logger.warning("python-dotenv package not available, skipping .env loading")
    except Exception as e:
        logger.warning(f"Could not load .env file: {str(e)}")

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
