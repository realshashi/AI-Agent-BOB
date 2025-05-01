import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

BAXUS_API_BASE_URL = "https://services.baxus.co/api"

def get_user_bar_data(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a user's bar collection data from the BAXUS API.
    
    Args:
        username: The BAXUS username for which to retrieve data
        
    Returns:
        Dictionary containing the user's bar data or None if an error occurs
    """
    endpoint = f"{BAXUS_API_BASE_URL}/bar/user/{username}"
    headers = {"Content-Type": "application/json"}
    
    try:
        logger.debug(f"Fetching bar data for user: {username}")
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            logger.debug(f"Successfully retrieved data for user: {username}")
            # Format the response for our app expecting a specific structure
            return {"bar": user_data}
        else:
            logger.error(f"Failed to retrieve user data: Status {response.status_code}, Response: {response.text}")
            return None
            
    except requests.RequestException as e:
        logger.exception(f"API request error for user {username}: {str(e)}")
        return None
    except ValueError as e:
        logger.exception(f"JSON parsing error for user {username}: {str(e)}")
        return None
