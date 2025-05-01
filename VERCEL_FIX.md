# Fixing Vercel Deployment Issues for Bob the Whisky Expert

This guide provides detailed steps to fix deployment issues with Vercel's serverless functions.

## Issue: "ModuleNotFoundError: No module named 'dotenv'"

The error occurs because Vercel's build environment doesn't correctly install or handle the `python-dotenv` package. Here are two different approaches to solve this:

### Solution 1: Use the Simplified Vercel API Only (Recommended)

This approach creates a minimal API endpoint specifically for Vercel:

1. **Rename files for clarity:**
   ```bash
   mv vercel.json vercel-full.json
   mv vercel-minimal.json vercel.json
   ```

2. **Deploy to Vercel with the new configuration:**
   This configuration uses only the minimal `api/vercel.py` file which has no external dependencies beyond Flask.

3. **Testing after deployment:**
   - Check `/api/status` - Should return a JSON status response
   - Test `/api/chat` with a POST request containing `{"message": "What's a good smoky whisky?"}`
   
### Solution 2: Fix the Full Application (Advanced)

If you want to deploy the complete application:

1. **Modify vercel_requirements.txt to explicitly specify package versions:**
   ```
   flask==3.0.0
   python-dotenv==1.0.0
   ```

2. **Update vercel.json to use pip's `--no-cache-dir` option:**
   ```json
   "installCommand": "pip install --no-cache-dir -r vercel_requirements.txt",
   ```

3. **Add a package.json file for Node.js runtime hints:**
   ```json
   {
     "name": "bob-whisky-expert",
     "version": "1.0.0",
     "engines": {
       "node": ">=14"
     }
   }
   ```

4. **Clear build cache on Vercel:**
   In the Vercel dashboard, go to your project settings, and delete any cached builds.

## Testing Your Deployment

After deploying, test the following endpoints:

- `/_debug` - Shows environment information for debugging
- `/api/status` - API status endpoint
- `/api/chat` - Chat API (POST request)

## Fallback Mode

If you continue to have issues, you can deploy just the API layer:

1. Use the `vercel-minimal.json` configuration (rename to `vercel.json`)
2. Deploy only the API endpoint
3. Configure your frontend to work with the API directly

## Common Vercel Deployment Issues:

1. **Cold Starts**: Serverless functions can have a delay on first request
2. **Function Timeout**: Default is 10 seconds - increase in vercel.json if needed
3. **Memory Limits**: Default is 1024MB - increase for larger applications
4. **Missing Dependencies**: Vercel might fail to install some packages
5. **Environment Variables**: Must be set in Vercel dashboard, not just in .env files

## Important Note on Database Access

If your application uses a database:

1. Vercel Functions work best with serverless databases (like MongoDB Atlas, Fauna, PlanetScale)
2. SQLite won't work in production (read-only filesystem)
3. Set up proper database connection string in Vercel environment variables