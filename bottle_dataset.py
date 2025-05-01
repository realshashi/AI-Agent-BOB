import pandas as pd
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# For now, we'll simulate the bottle dataset
# In a real implementation, this would load from a database or CSV file
def get_bottle_dataset() -> pd.DataFrame:
    """
    Loads the 501-bottle dataset.
    
    Returns:
        A pandas DataFrame containing all bottles with their attributes
    """
    # This is a placeholder. In a real implementation, this would load the actual dataset.
    # For demonstration purposes, we'll create a simplified mock dataset structure
    data = {
        'id': list(range(1, 502)),
        'name': [f"Whisky {i}" for i in range(1, 502)],
        'spirit_type': ['Single Malt', 'Bourbon', 'Rye', 'Blended Scotch', 'Japanese'] * 100 + ['Single Malt'],
        'region': ['Scotland-Islay', 'Scotland-Speyside', 'America', 'Japan', 'Ireland'] * 100 + ['Scotland-Highland'],
        'abv': [40 + (i % 20) for i in range(1, 502)],
        'msrp': [50 + (i % 200) for i in range(1, 502)],
        'fair_price': [60 + (i % 250) for i in range(1, 502)],
        'total_score': [80 + (i % 20) for i in range(1, 502)],
        'flavor_profile_peated': [(i % 5) * 20 for i in range(1, 502)],
        'flavor_profile_sherried': [(i % 4) * 25 for i in range(1, 502)],
        'flavor_profile_fruity': [(i % 3) * 30 for i in range(1, 502)],
        'flavor_profile_spicy': [(i % 6) * 15 for i in range(1, 502)],
        'brand_id': [f"Brand-{(i % 50) + 1}" for i in range(1, 502)],
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add more flavor profiles as columns
    df['flavor_profile_smoky'] = df['flavor_profile_peated'] * 0.8
    df['flavor_profile_vanilla'] = 100 - df['flavor_profile_peated']
    df['flavor_profile_caramel'] = (df['flavor_profile_sherried'] + df['flavor_profile_vanilla']) / 2
    
    # Convert to categorical types for efficiency
    df['spirit_type'] = pd.Categorical(df['spirit_type'])
    df['region'] = pd.Categorical(df['region'])
    
    return df

def get_bottle_by_id(bottle_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific bottle by ID from the dataset.
    
    Args:
        bottle_id: The ID of the bottle to retrieve
        
    Returns:
        Dictionary containing the bottle data or None if not found
    """
    df = get_bottle_dataset()
    bottle = df[df['id'] == bottle_id]
    
    if bottle.empty:
        return None
    
    return bottle.iloc[0].to_dict()

def get_bottles_by_region(region: str) -> List[Dict[str, Any]]:
    """
    Retrieves bottles from a specific region.
    
    Args:
        region: The whisky region to filter by
        
    Returns:
        List of dictionaries containing bottle data
    """
    df = get_bottle_dataset()
    bottles = df[df['region'] == region]
    
    return bottles.to_dict('records')

def get_bottles_by_spirit_type(spirit_type: str) -> List[Dict[str, Any]]:
    """
    Retrieves bottles of a specific spirit type.
    
    Args:
        spirit_type: The spirit type to filter by
        
    Returns:
        List of dictionaries containing bottle data
    """
    df = get_bottle_dataset()
    bottles = df[df['spirit_type'] == spirit_type]
    
    return bottles.to_dict('records')

def get_bottles_by_price_range(min_price: float, max_price: float) -> List[Dict[str, Any]]:
    """
    Retrieves bottles within a specific price range.
    
    Args:
        min_price: The minimum price
        max_price: The maximum price
        
    Returns:
        List of dictionaries containing bottle data
    """
    df = get_bottle_dataset()
    bottles = df[(df['msrp'] >= min_price) & (df['msrp'] <= max_price)]
    
    return bottles.to_dict('records')
