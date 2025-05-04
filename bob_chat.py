import os
import logging
import hashlib
from openai import OpenAI
from typing import Dict, List, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Simple response cache to avoid repeated API calls
response_cache = {
    # Pre-populated responses for common questions
    "8d30f95900b08658ccd78bc1fbabe5e0": "For smoky flavors, I'd recommend Islay whiskies like Laphroaig, Ardbeg, or Lagavulin. They're known for their intense peat smoke character. If you want something less intense, try Highland Park or Talisker for a more balanced approach to smokiness.",
    "a5db6807fb4aa3b8b6a019f28d4f30b0": "The main whisky regions in Scotland are: Highlands, Lowlands, Speyside, Islay, and Campbeltown. Each has distinctive characteristics - Highlands are often full-bodied, Speyside known for fruity elegance, Islay for peaty smoke, Lowlands for lighter styles, and Campbeltown for a unique maritime character.",
    "c15f957a46e787c35b5a0b933e3e4e5c": "To start exploring whisky, I recommend trying these approachable options: Glenmorangie Original (Highland), Monkey Shoulder (Blended Scotch), Buffalo Trace (Bourbon), or Jameson (Irish). These are smooth, well-balanced, and give you a good introduction to different styles without overwhelming your palate.",
    "61afc5979b68f02e0b044be70eb4be24": "The difference between whisky and whiskey is primarily about origin. 'Whisky' (no 'e') is typically used in Scotland, Canada, and Japan. 'Whiskey' (with an 'e') is used in Ireland and the United States. The spelling reflects different traditions and sometimes different production methods."
}

# Initialize the OpenAI client (lazily to avoid API calls unless needed)
api_key = os.environ.get("OPENAI_API_KEY")
client = None

def get_openai_client():
    global client, api_key
    if client is None:

        
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            return None
        else:
            logger.info("OpenAI API key found in environment variables")
            client = OpenAI(api_key=api_key)
    return client

def add_to_cache(question: str, answer: str) -> None:
    """Add a question and answer to the cache"""
    key = hashlib.md5(question.lower().strip().encode()).hexdigest()
    response_cache[key] = answer
    logger.info(f"Added to cache: {key} - Question: {question}")

# Add more predefined responses to cache
common_questions = {
    "What's the best whisky under $50?": 
        "For under $50, I recommend Buffalo Trace or Wild Turkey 101 for bourbon fans, Monkey Shoulder for a smooth blended Scotch, or Jameson Black Barrel for Irish whiskey enthusiasts. All offer exceptional quality at affordable prices.",
    
    "How should I taste whisky properly?": 
        "To properly taste whisky: 1) Look at the color, 2) Nose it gently, 3) Take a small sip and let it coat your mouth, 4) Consider adding a few drops of water to open up flavors, 5) Think about the finish and lingering tastes. Take your time and enjoy the experience!",
    
    "What food pairs well with whisky?": 
        "Whisky pairs wonderfully with dark chocolate, aged cheeses like cheddar, smoked salmon, grilled meats, and even desserts like caramel or fruit tarts. The key is matching intensity - lighter whiskies with delicate foods, robust whiskies with more flavorful dishes.",
    
    "What is a single malt?": 
        "A single malt whisky is made from 100% malted barley at one distillery. Unlike blended whiskies, which combine spirits from multiple distilleries, single malts showcase the unique character of their distillery's production style, water source, and maturation environment."
}

# Add common questions to cache
for question, answer in common_questions.items():
    add_to_cache(question, answer)

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

def add_to_cache(question: str, answer: str) -> None:
    """Add a question and answer to the cache"""
    key = hashlib.md5(question.lower().strip().encode()).hexdigest()
    response_cache[key] = answer
    logger.info(f"Added to cache: {key} - Question: {question}")
    
def generate_cache_key(messages: List[Dict[str, str]]) -> Optional[str]:
    """Generate a cache key based on the user's message content"""
    # Only use the last user message for caching to keep it simple
    for message in reversed(messages):
        if message["role"] == "user":
            # Create hash of the message content
            return hashlib.md5(message["content"].lower().strip().encode()).hexdigest()
    return None

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
    
    # Check if we have a cached response for this question
    cache_key = generate_cache_key(messages)
    if cache_key and cache_key in response_cache:
        logger.info(f"Using cached response for question: {cache_key}")
        return response_cache[cache_key]
    
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
        # Get the OpenAI client (lazy initialization)
        client = get_openai_client()
        if client is None:
            return "I apologize, but I'm having trouble connecting to my whisky knowledge base. The API key is missing. Please try again later."
            
        # Call the OpenAI API with optimized settings for free plan
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use more economical model for free plan
            messages=conversation,
            temperature=0.7,  # Balanced between creativity and consistency
            max_tokens=250,  # Reduced token usage
            presence_penalty=0.6,  # Encourage model to be more concise
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content
        
        # Cache the response if we have a valid cache key
        if cache_key:
            response_cache[cache_key] = response_text
            logger.info(f"Cached response for question: {cache_key}")
            
        return response_text
    
    except Exception as e:
        error_str = str(e)
        logger.exception(f"Error calling OpenAI API: {error_str}")
        
        if "insufficient_quota" in error_str or "exceeded your current quota" in error_str:
            return "I apologize, but I'm not available right now due to API quota limitations. Please contact the administrator to update the OpenAI API key with additional credits."
        else:
            return "I apologize, but I'm having trouble connecting to my whisky knowledge base at the moment. Please try again shortly."