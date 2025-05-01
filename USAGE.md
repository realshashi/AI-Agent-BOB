# User Guide: Bob the Whisky Expert

This guide explains how to use Bob the Whisky Expert to discover personalized whisky recommendations and interact with Bob, your AI whisky assistant.

## Getting Started

### Accessing the Application

1. Open your web browser and go to the application URL (locally: http://localhost:5000)
2. You will be presented with the welcome page where you can enter your BAXUS username

### Entering Your BAXUS Username

1. On the welcome page, you'll find a form asking for your BAXUS username
2. Enter your BAXUS username (e.g., "carriebaxus") in the input field
3. Click the "Get Recommendations" button
4. If you don't have a BAXUS account, the application will not be able to retrieve your collection (future versions may include a demo mode)

## Viewing Recommendations

### Understanding Your Preferences

After submitting your BAXUS username, you'll be taken to the recommendations page that shows:

1. **Whisky Preferences**: Analysis of your current whisky collection, including:
   - Preferred regions (e.g., Speyside, Islay)
   - Favorite spirit types (e.g., Single Malt, Bourbon)
   - Typical price range
   - ABV preferences
   - Flavor profile tendencies

2. **Your Recommendations**: A list of personalized whisky bottle recommendations based on your preferences

### Recommendation Details

Each recommendation includes:

- Bottle name and distillery
- Region and spirit type
- ABV percentage
- Rating score (if available)
- Price information (MSRP and fair price)
- Flavor profile visualization
- Personalized explanation of why this bottle was recommended for you

### Navigation

- To get recommendations for a different BAXUS username, click the "Try Another Username" button at the bottom of the page
- To interact with Bob the Whisky Expert, use the chat widget in the bottom right corner

## Chatting with Bob

### Opening the Chat

1. On the recommendations page, you'll see the "Chat with BOB" widget in the bottom right corner
2. The chat window may be minimized initially; click on the header to expand it

### Asking Questions

You can ask Bob about:

- Specific whiskies or distilleries
- Whisky regions and production methods
- Flavor profiles and tasting notes
- Price comparisons and value recommendations
- Food pairings and serving suggestions
- Your current collection and preferences

### Example Questions

Try asking Bob questions like:
- "What whisky should I try if I like smoky flavors?"
- "Tell me about Japanese whisky"
- "Can you recommend a good whisky under $50?"
- "What's the difference between bourbon and scotch?"
- "Which whiskies pair well with chocolate?"
- "What's special about Islay whiskies?"

### Using Suggestions

1. Click the "Suggestions" link at the bottom of the chat input area
2. Select from the dropdown menu of common whisky questions
3. The selected question will be sent to Bob automatically

### Resetting the Chat

If you want to start a fresh conversation:
1. Click the "Reset" link at the bottom of the chat input area
2. This will clear your chat history with Bob
3. Bob will respond with a new welcome message

## Privacy and Data Usage

- The application only accesses your public BAXUS data
- Your chat history is stored temporarily in your browser session
- No personal information is permanently stored

## Troubleshooting

### Chat Not Working

If the chat feature isn't responding:
- The OpenAI API key may be missing or invalid
- There could be connectivity issues to the OpenAI service
- You may have reached the rate limit for API calls

### Missing Recommendations

If you're not seeing any recommendations:
- Verify that you entered your BAXUS username correctly
- Ensure your BAXUS collection has at least a few bottles
- Check if the BAXUS API is reachable

### Browser Issues

For the best experience:
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Enable JavaScript
- Allow cookies for session management