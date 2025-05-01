# Installation Guide for Bob the Whisky Expert

This guide provides detailed instructions for setting up and running Bob the Whisky Expert on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bob-whisky-expert.git
cd bob-whisky-expert
```

### 2. Install Required Packages

Install the following required packages:

```bash
pip install flask
pip install flask-sqlalchemy
pip install gunicorn
pip install python-dotenv
pip install openai
pip install requests
pip install pandas
pip install numpy
pip install scikit-learn
pip install email-validator
pip install trafilatura
pip install psycopg2-binary
```

Alternatively, on Replit, you can use the package management tool to install these packages.

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```plaintext
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Session configuration
SESSION_SECRET=your_session_secret_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key. This is required for the chat functionality.

To get an OpenAI API key:
1. Sign up or log in at [OpenAI](https://platform.openai.com/signup)
2. Go to your API settings
3. Create a new API key
4. Copy the key and paste it into your `.env` file

### 4. Start the Application

Run the application using:

```bash
python main.py
```

For production environments, use gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### 5. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

If running on Replit, click the "Show" button to open the web application.

## Troubleshooting

### OpenAI API Key Issues

If you see error messages about the OpenAI API key:
- Make sure you've set up the `.env` file correctly
- Check that the API key is valid and has not expired
- Verify that your OpenAI account has sufficient credits

### Database Issues

If you encounter database-related errors:
- Ensure all SQL-related packages are installed
- Check the database connection settings in the application

### Package Installation Problems

If you have issues installing packages:
- Make sure you're using a compatible Python version
- Try upgrading pip: `pip install --upgrade pip`
- On Replit, use the packager tool instead of pip commands

## Updating the Application

To update the application to the latest version:

```bash
git pull origin main
```

Then restart the application.

## Support

If you need additional help with installation or configuration, please:
- Check the main README.md for more information
- Open an issue on the GitHub repository
- Contact the maintainers through the project's contact information