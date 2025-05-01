# Bob the Whisky Expert

Bob the Whisky Expert is an AI-powered whisky recommendation platform that provides personalized bottle suggestions through advanced machine learning algorithms and interactive user experiences.

![Bob the Whisky Expert](static/images/bob-avatar.svg)

## Features

- **Personal Whisky Recommendations**: Analyzes user whisky collection to provide tailored bottle suggestions
- **Advanced Recommendation Engine**: Uses collaborative filtering and preference analysis
- **Interactive Chat**: Talk directly with "Bob" about whisky recommendations and questions
- **BAXUS Integration**: Connects with the BAXUS API to fetch user collection data
- **Detailed Flavor Profiles**: Visual representation of whisky flavor characteristics
- **Price Analysis**: Recommendations based on your typical spending patterns

## Technical Requirements

### Python Version

- Python 3.11 or higher

### Dependencies

- Flask 3.0.0: Web framework
- Flask-SQLAlchemy 3.1.1: Database ORM
- OpenAI 1.3.8: AI integration
- NumPy 1.24.3 & Pandas 2.0.3: Data processing
- Scikit-learn 1.3.0: Machine learning
- Gunicorn 20.1.0: Production server
- Additional dependencies are listed in `requirements.txt`

### Local Setup

1. Clone the repository
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the development server:
   ```bash
   python main.py
   ```

### Docker Deployment

1. Clone the repository
2. Make sure Docker and Docker Compose are installed
3. Create a `.env` file with your environment variables:
   ```
   OPENAI_API_KEY=your_key_here
   SESSION_SECRET=your_secret_here
   ```
4. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
5. The application will be available at `http://localhost:5000`

Note: The SQLite database file (bob_cache.db) is persisted through a Docker volume.

## Environment Variables

Required environment variables:

- `OPENAI_API_KEY`: Required for the chat functionality
- `FLASK_ENV`: Set to 'development' or 'production'
- `FLASK_DEBUG`: Set to 'True' for development
- `SECRET_KEY`: Flask secret key for securing sessions
- `SESSION_SECRET`: Session security key

## Testing

### API Testing

Run the API tests to verify endpoints are working correctly:

```bash
python test_vercel_api.py
```

This will test:

- Status endpoint (/api/status)
- Chat endpoint (/api/chat)
- Debug endpoint (development only)

Note: By default, tests run against localhost. Edit BASE_URL in test_vercel_api.py to test against deployed endpoints.

## Usage Guide

### Basic Usage

1. Enter your BAXUS username on the welcome page
2. View your personalized recommendations and preference analysis
3. Use the chat widget to interact with Bob

### Chat Features

- Ask about specific whiskies or distilleries
- Get recommendations based on flavor preferences
- Learn about whisky regions and types
- Get price comparisons and value suggestions

Example questions:

- "What whisky should I try if I like smoky flavors?"
- "Tell me about Japanese whisky"
- "Good whisky under $50?"
- "What's the difference between bourbon and scotch?"

## Troubleshooting

### API Issues

- Verify OpenAI API key is valid and not expired
- Check OpenAI account has sufficient credits
- Ensure BAXUS API is accessible

### Application Issues

- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Enable JavaScript for full functionality
- Clear browser cache if experiencing display issues
- Verify your BAXUS username is correct

For more detailed information, see:

- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE.md)

## License

[MIT License](LICENSE)

## Acknowledgments

- Built with Flask, OpenAI API, and Bootstrap
- Uses the BAXUS API for collection data
- Whisky dataset includes comprehensive bottle information
