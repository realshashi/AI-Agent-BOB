import os
import logging
from openai import OpenAI
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Initialize the OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.error("OpenAI API key not found in environment variables")
else:
    logger.info("OpenAI API key found in environment variables")
client = OpenAI(api_key=api_key)

# BOB's personality and knowledge system prompt
BOB_SYSTEM_PROMPT = """
You are "Bob the Whisky Expert," a friendly and knowledgeable AI assistant specializing in whisky recommendations.

Knowledge and Personality:
- You're an expert on whiskey regions, distilleries, tasting notes, and production methods
- You have deep knowledge of whisky brands, styles, and flavor profiles
- Your tone is friendly, enthusiastic, and approachable - like a knowledgeable friend
- You respect all budgets and preferences
- You provide clear explanations that educate while recommending

When responding to users:
1. Be helpful and specific in your whisky recommendations
2. Explain why you're recommending specific whiskies based on flavor profiles, regions, or styles
3. If a user is new to whisky, guide them with approachable suggestions
4. For connoisseurs, provide insights on rare or complex expressions
5. Always respect budget constraints when mentioned
6. Include information about tasting notes, finish, and food pairings when appropriate

IMPORTANT: While you're an AI and don't actually drink whisky, respond as if you have experienced these spirits professionally through your expert knowledge.
"""

def chat_with_bob(messages: List[Dict[str, str]], username: Optional[str] = None, 
                user_preferences: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a response from Bob the Whisky Expert.
    
    Args:
        messages: List of message objects with 'role' and 'content'
        username: Optional username for personalized responses
        user_preferences: Optional user preferences from BAXUS collection analysis
        
    Returns:
        Bob's response to the user's query
    """
    # Check if API key is available again (belt and suspenders)
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OpenAI API key not available in environment when chat_with_bob was called")
        return "I apologize, but I'm having trouble connecting to my whisky knowledge base. The API key is missing. Please try again later."
    
    # Start with the system message defining Bob's persona
    system_message = {"role": "system", "content": BOB_SYSTEM_PROMPT}
    
    # If we have user preferences, add them to the system message for context
    if username and user_preferences:
        preference_info = f"\nAdditional context about {username}:\n"
        
        # Add region preferences if available
        if 'preferred_regions' in user_preferences and user_preferences['preferred_regions']:
            regions = []
            for region, value in user_preferences['preferred_regions'].items():
                if value > 10:  # Only consider significant preferences
                    regions.append(f"{region} ({value:.1f}%)")
            if regions:
                preference_info += f"- Preferred regions: {', '.join(regions)}\n"
        
        # Add spirit type preferences if available
        if 'spirit_types' in user_preferences and user_preferences['spirit_types']:
            spirits = []
            for spirit, value in user_preferences['spirit_types'].items():
                if value > 10:  # Only consider significant preferences
                    spirits.append(f"{spirit} ({value:.1f}%)")
            if spirits:
                preference_info += f"- Preferred spirit types: {', '.join(spirits)}\n"
        
        # Add flavor profile preferences if available
        if 'flavor_profiles' in user_preferences and user_preferences['flavor_profiles']:
            flavors = []
            for flavor, value in user_preferences['flavor_profiles'].items():
                if value > 30:  # Only consider strong flavor preferences
                    flavors.append(f"{flavor}")
            if flavors:
                preference_info += f"- Preferred flavor profiles: {', '.join(flavors)}\n"
        
        # Add price preferences if available
        if 'average_bottle_price' in user_preferences:
            avg_price = user_preferences['average_bottle_price']
            preference_info += f"- Average bottle price: ${avg_price:.2f}\n"
        
        # Update the system message with user preference information
        system_message["content"] += preference_info
    
    # Prepare the full conversation history with the system message first
    conversation = [system_message] + messages
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Use the latest model
            messages=conversation,
            temperature=0.7,  # Balanced between creativity and consistency
            max_tokens=500,  # Reasonable response length
        )
        
        # Extract and return the response content
        return response.choices[0].message.content
    
    except Exception as e:
        logger.exception(f"Error calling OpenAI API: {str(e)}")
        return "I apologize, but I'm having trouble connecting to my whisky knowledge base at the moment. Please try again shortly."