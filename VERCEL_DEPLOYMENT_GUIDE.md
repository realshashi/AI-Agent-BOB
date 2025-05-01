# Vercel Serverless Deployment Guide for Bob the Whisky Expert

This guide provides detailed steps for deploying the Bob the Whisky Expert application on Vercel's serverless platform.

## Deployment Architecture

The application has been restructured for serverless deployment with:

1. **API Endpoints**: Lighter serverless functions in the `/api` directory
2. **Memory Caching**: Adapted for stateless environments
3. **Rate Limiting**: Implemented in-memory to stay within OpenAI API constraints 
4. **Error Handling**: Enhanced for serverless execution model

## Prerequisites

Before deploying, ensure you have:

- A [Vercel account](https://vercel.com/signup)
- A valid [OpenAI API key](https://platform.openai.com/account/api-keys)
- Your project code in a Git repository (GitHub, GitLab, or Bitbucket)

## Step-by-Step Deployment Instructions

### 1. Push Your Code to a Git Repository

First, push your code to a git repository that Vercel can access:

```bash
git add .
git commit -m "Prepare Bob the Whisky Expert for Vercel deployment"
git push
```

### 2. Import Your Project on Vercel

1. Log in to your Vercel account
2. Click "Add New..." and select "Project"
3. Import your Git repository
4. Select the repository containing Bob the Whisky Expert

### 3. Configure Environment Variables

In the Vercel deployment settings, add these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SESSION_SECRET`: A secure random string for session encryption
- `VERCEL`: Set to `1` (this enables Vercel-specific optimizations)

### 4. Deploy Your Project

Click "Deploy" to start the deployment process. 

### 5. Test Your Deployment

After deployment completes:

1. Visit the deployed URL provided by Vercel
2. Test the application's functionality
3. Try the API status endpoint: `https://your-project.vercel.app/api/status`
4. Test the chat API with the test page: `https://your-project.vercel.app/vercel-test.html`

## Understanding the Serverless Structure

This project is designed to work optimally in a serverless environment:

### Main Files for Vercel

- **vercel.json**: Configures build settings and routes
- **api/index.py**: Main entry point for web application
- **api/whisky.py**: Dedicated API for chat functionality
- **bob_chat.py**: Modified to use memory caching in serverless environment

### Key API Endpoints

- **/** - Main web application
- **/api/status** - Health check endpoint
- **/api/chat** - JSON API for chat functionality (POST request)

## Troubleshooting

### If you see "FUNCTION_INVOCATION_FAILED" errors:

1. **Check environment variables**: Ensure OPENAI_API_KEY is properly set in Vercel dashboard
2. **Check API limits**: Verify you haven't exceeded OpenAI rate limits
3. **Review logs**: Check Vercel Function Logs for detailed error information
4. **Test locally**: Use the Vercel CLI to test functions locally before deployment

### Database Issues

The application uses in-memory caching when deployed on Vercel due to the read-only filesystem in serverless functions. If you need persistent storage, consider using:

- Vercel KV (for Redis-like storage)
- MongoDB Atlas or similar database-as-a-service
- Fauna or other serverless-friendly databases

## Performance Optimization Tips

1. **Cold Starts**: The first request may be slow due to cold starts. Consider setting up a ping service to keep functions warm.
2. **Memory Usage**: Keep an eye on memory usage in the Vercel dashboard.
3. **API Limits**: Monitor OpenAI API usage to avoid unexpected costs or rate limit issues.

## Need Help?

If you encounter issues with your Vercel deployment, consult:

- [Vercel Documentation](https://vercel.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)