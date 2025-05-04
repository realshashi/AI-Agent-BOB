import os
import logging
import hashlib
import time
import sqlite3
from datetime import datetime, timedelta
from openai import OpenAI
from typing import Dict, List, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Initialize rate limiting variables
RATE_LIMIT = 3  # 3 requests per minute
request_timestamps = []

# Memory-based cache for Vercel's serverless environment
# This is needed because Vercel's filesystem is read-only in production
memory_cache = {}

# Initialize SQLite for persistent caching in development only
def init_cache_db():
    try:
        # Check if we're in a serverless environment (like Vercel)
        is_vercel = os.environ.get('VERCEL') == '1'
        
        if not is_vercel:
            conn = sqlite3.connect('bob_cache.db')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS response_cache (
                    question_hash TEXT PRIMARY KEY,
                    question TEXT,
                    answer TEXT,
                    created_at TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("SQLite cache initialized for development")
        else:
            logger.info("Running in serverless mode - using memory cache only")
    except Exception as e:
        logger.warning(f"Could not initialize SQLite DB: {str(e)}. Using memory cache only.")

# Initialize cache DB
init_cache_db()

# Function to check if we're within rate limits
def check_rate_limit():
    global request_timestamps
    current_time = time.time()
    
    # Remove timestamps older than 1 minute
    request_timestamps = [t for t in request_timestamps if current_time - t < 60]
    
    # Check if we're at the rate limit
    if len(request_timestamps) >= RATE_LIMIT:
        return False
    
    # Add current timestamp and return True (we're within limits)
    request_timestamps.append(current_time)
    return True

# Get response from cache
def get_from_cache(question_hash):
    # First check memory cache
    if question_hash in memory_cache:
        logger.info(f"Memory cache hit for hash: {question_hash}")
        return memory_cache[question_hash]
    
    # Then try SQLite cache if not in serverless mode
    is_vercel = os.environ.get('VERCEL') == '1'
    if not is_vercel:
        try:
            conn = sqlite3.connect('bob_cache.db')
            c = conn.cursor()
            c.execute('SELECT answer FROM response_cache WHERE question_hash = ?', (question_hash,))
            result = c.fetchone()
            conn.close()
            
            if result:
                # Also store in memory cache for future lookups
                memory_cache[question_hash] = result[0]
                logger.info(f"SQLite cache hit for hash: {question_hash}")
                return result[0]
        except Exception as e:
            logger.warning(f"Error retrieving from SQLite cache: {str(e)}")
    
    return None

# Add response to cache
def add_to_cache(question: str, answer: str) -> None:
    """Add a question and answer to the cache"""
    question_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    # Always add to memory cache
    memory_cache[question_hash] = answer
    
    # Also try to add to SQLite if not in serverless mode
    is_vercel = os.environ.get('VERCEL') == '1'
    if not is_vercel:
        try:
            conn = sqlite3.connect('bob_cache.db')
            c = conn.cursor()
            c.execute(
                'INSERT OR REPLACE INTO response_cache (question_hash, question, answer, created_at) VALUES (?, ?, ?, ?)',
                (question_hash, question, answer, datetime.now())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Error saving to SQLite cache: {str(e)}")
    
    logger.info(f"Added to cache: {question_hash} - Question: {question}")

def generate_cache_key(messages: List[Dict[str, str]]) -> Optional[str]:
    """Generate a cache key based on the user's message content"""
    # Only use the last user message for caching to keep it simple
    for message in reversed(messages):
        if message["role"] == "user":
            # Create hash of the message content
            return hashlib.md5(message["content"].lower().strip().encode()).hexdigest()
    return None

# Initialize the OpenAI client (lazily to avoid API calls unless needed)
client = None

def get_openai_client():
    """Get or initialize the OpenAI client"""
    global client
    
    # Only create the client once
    if client is None:
        # Get the API key from environment (checking each time to handle serverless environment)
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            return None
        else:
            logger.info("OpenAI API key found in environment")
            try:
                client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
                return None
    
    return client

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

# Pre-populate common questions
common_questions = {
    "What whisky should I try if I like smoky flavors?": 
        "For smoky flavors, I'd recommend Islay whiskies like Laphroaig, Ardbeg, or Lagavulin. They're known for their intense peat smoke character. If you want something less intense, try Highland Park or Talisker for a more balanced approach to smokiness.",
    
    "What are the main whisky regions?": 
        "The main whisky regions in Scotland are: Highlands, Lowlands, Speyside, Islay, and Campbeltown. Each has distinctive characteristics - Highlands are often full-bodied, Speyside known for fruity elegance, Islay for peaty smoke, Lowlands for lighter styles, and Campbeltown for a unique maritime character.",
    
    "I'm new to whisky. What should I try?": 
        "To start exploring whisky, I recommend trying these approachable options: Glenmorangie Original (Highland), Monkey Shoulder (Blended Scotch), Buffalo Trace (Bourbon), or Jameson (Irish). These are smooth, well-balanced, and give you a good introduction to different styles without overwhelming your palate.",
    
    "What's the difference between whisky and whiskey?": 
        "The difference between whisky and whiskey is primarily about origin. 'Whisky' (no 'e') is typically used in Scotland, Canada, and Japan. 'Whiskey' (with an 'e') is used in Ireland and the United States. The spelling reflects different traditions and sometimes different production methods.",
        
    "What's the best whisky under $50?": 
        "For under $50, I recommend Buffalo Trace or Wild Turkey 101 for bourbon fans, Monkey Shoulder for a smooth blended Scotch, or Jameson Black Barrel for Irish whiskey enthusiasts. All offer exceptional quality at affordable prices.",
    
    "How should I taste whisky properly?": 
        "To properly taste whisky: 1) Look at the color, 2) Nose it gently, 3) Take a small sip and let it coat your mouth, 4) Consider adding a few drops of water to open up flavors, 5) Think about the finish and lingering tastes. Take your time and enjoy the experience!",
    
    "What food pairs well with whisky?": 
        "Whisky pairs wonderfully with dark chocolate, aged cheeses like cheddar, smoked salmon, grilled meats, and even desserts like caramel or fruit tarts. The key is matching intensity - lighter whiskies with delicate foods, robust whiskies with more flavorful dishes.",
    
    "What is a single malt?": 
        "A single malt whisky is made from 100% malted barley at one distillery. Unlike blended whiskies, which combine spirits from multiple distilleries, single malts showcase the unique character of their distillery's production style, water source, and maturation environment.",
        
    "What's a good gift whisky?": 
        "For a gift, Macallan 12 is always impressive with its rich sherry character, Balvenie 14 Caribbean Cask offers unique rum-influenced flavors, and Hibiki Harmony presents beautifully with its elegant bottle and smooth Japanese blending style. All are special without being overly challenging for most palates.",
        
    "What's your favorite whisky?": 
        "While I appreciate many different whiskies, I particularly enjoy Springbank 15 for its complex character combining light smoke, fruit, and maritime notes, all from traditional production methods. It represents the unique Campbeltown style beautifully."
}

# Add common questions to cache
for question, answer in common_questions.items():
    add_to_cache(question, answer)

def get_rule_based_response(user_message):
    """Attempt to match user message to predefined responses without using API"""
    # Convert message to lowercase for case-insensitive matching
    message_lower = user_message.lower().strip()
    
    # Keyword-based matching for common questions
    if "smoky" in message_lower or "peaty" in message_lower or "smokey" in message_lower:
        return common_questions["What whisky should I try if I like smoky flavors?"]
        
    if "region" in message_lower:
        return common_questions["What are the main whisky regions?"]
        
    if "new" in message_lower and ("whisky" in message_lower or "whiskey" in message_lower):
        return common_questions["I'm new to whisky. What should I try?"]
        
    if "whisky" in message_lower and "whiskey" in message_lower and "difference" in message_lower:
        return common_questions["What's the difference between whisky and whiskey?"]
        
    if ("under" in message_lower and "$50" in message_lower) or ("cheap" in message_lower):
        return common_questions["What's the best whisky under $50?"]
        
    if "taste" in message_lower or "tasting" in message_lower:
        return common_questions["How should I taste whisky properly?"]
        
    if "food" in message_lower or "pair" in message_lower or "pairing" in message_lower:
        return common_questions["What food pairs well with whisky?"]
        
    if "single malt" in message_lower:
        return common_questions["What is a single malt?"]
        
    if "gift" in message_lower or "present" in message_lower:
        return common_questions["What's a good gift whisky?"]
        
    if "favorite" in message_lower or "best" in message_lower:
        return common_questions["What's your favorite whisky?"]
        
    # No match found
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
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OpenAI API key not available in environment when chat_with_bob was called")
        return "I apologize, but I'm having trouble connecting to my whisky knowledge base. The API key is missing. Please try again later."
    
    # Get the last user message
    user_message = None
    for message in reversed(messages):
        if message["role"] == "user":
            user_message = message["content"]
            break
    
    if not user_message:
        return "I'm sorry, I couldn't understand your question. Please try asking again."
    
    # Check if we have a cached response
    cache_key = generate_cache_key(messages)
    if cache_key:
        cached_response = get_from_cache(cache_key)
        if cached_response:
            return cached_response
    
    # Try rule-based response first to avoid API call
    rule_based_response = get_rule_based_response(user_message)
    if rule_based_response:
        # Still cache this response
        if cache_key:
            add_to_cache(user_message, rule_based_response)
        return rule_based_response
    
    # Check if we're within rate limits
    if not check_rate_limit():
        logger.warning("Rate limit exceeded, using fallback response")
        return ("I'm currently helping several other customers right now. To avoid delays, "
                "I can provide some general whisky information: Scotch whisky is primarily "
                "categorized into five regions: Highlands, Speyside, Islay, Lowlands, and "
                "Campbeltown, each with distinctive flavor profiles. Please try your specific "
                "question again in a minute or browse our recommendations above.")
    
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
            
        # Call the OpenAI API with GPT-3.5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using standard GPT-3.5-turbo model
            messages=conversation,
            temperature=0.7,  # Balanced between creativity and consistency
            max_tokens=250,  # Reduced token usage
            presence_penalty=0.6,  # Encourage model to be more concise
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content
        
        # Cache the response
        if cache_key and user_message:
            add_to_cache(user_message, response_text)
            
        return response_text
    
    except Exception as e:
        error_str = str(e)
        logger.exception(f"Error calling OpenAI API: {error_str}")
        
        if "insufficient_quota" in error_str or "exceeded your current quota" in error_str:
            return "I apologize, but I'm not available right now due to API quota limitations. Please contact the administrator to update the OpenAI API key with additional credits."
        elif "invalid_api_key" in error_str:
            return "I apologize, but I'm having trouble connecting due to an invalid API key. Please contact the administrator to provide a valid OpenAI API key."
        elif "rate limit" in error_str.lower():
            return "I'm receiving many questions right now. Please try again in a minute or browse our recommendations above."
        else:
            return "I apologize, but I'm having trouble connecting to my whisky knowledge base at the moment. Please try again shortly."