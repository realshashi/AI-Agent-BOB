# Deploying Bob the Whisky Expert to Vercel

This guide will help you deploy the Bob the Whisky Expert application to Vercel's serverless platform.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. A valid [OpenAI API key](https://platform.openai.com/account/api-keys)
3. Git repository with your project code

## Deployment Steps

### 1. Push Your Code to a Git Repository

First, push your code to a GitHub, GitLab, or Bitbucket repository.

### 2. Import Your Project to Vercel

1. Log in to your Vercel account
2. Click "Add New..." and select "Project"
3. Import your Git repository
4. Select the repository containing Bob the Whisky Expert

### 3. Configure Environment Variables

In the Vercel deployment settings, add the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SESSION_SECRET`: A secure random string for session encryption
- `VERCEL`: Set to `1` to enable Vercel-specific optimizations
- `FLASK_DEBUG`: Set to `false` for production

### 4. Configure Framework Preset

1. In the "Build & Development Settings" section, set:
   - Framework Preset: `Other`
   - Build Command: Leave blank (uses default)
   - Output Directory: Leave blank (uses default)

### 5. Deploy Your Project

Click "Deploy" to start the deployment process. Vercel will build and deploy your application.

## Post-Deployment

After deployment, Vercel will provide you with a URL where your application is hosted. This is your Bob the Whisky Expert application's new home!

## Important Notes

- The application uses an in-memory cache for Vercel's serverless environment
- Session data is persisted through HTTP cookies
- For high-traffic applications, consider upgrading your Vercel plan
- If you encounter errors, check the Vercel logs for details

## Troubleshooting

- If the chat feature doesn't work, verify that your OpenAI API key is correctly set
- For database issues, ensure your PostgreSQL connection URL is valid
- For session issues, try clearing your browser cookies and restarting