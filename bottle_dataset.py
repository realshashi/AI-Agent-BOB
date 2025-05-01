import logging
import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def get_bottle_dataset() -> pd.DataFrame:
    """
    Loads the 500+ bottle dataset from JSON file
    
    Returns:
        A pandas DataFrame containing all bottles with their attributes
    """
    try:
        # Load the dataset from JSON
        json_path = os.path.join('static', 'data', 'bottles.json')
        logger.debug(f"Loading bottles from {json_path}")
        
        with open(json_path, 'r') as f:
            bottles = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(bottles)
        
        # Handle flavor_profile (convert from nested dict to separate columns)
        if 'flavor_profile' in df.columns:
            for bottle_idx, bottle in df.iterrows():
                if bottle['flavor_profile'] is not None:
                    for flavor, value in bottle['flavor_profile'].items():
                        col_name = f'flavor_profile_{flavor}'
                        if col_name not in df.columns:
                            df[col_name] = 0  # Initialize column if it doesn't exist
                        df.at[bottle_idx, col_name] = value
        
        # Make sure we have these fields
        if 'msrp' not in df.columns and 'avg_msrp' in df.columns:
            df['msrp'] = df['avg_msrp']
        
        logger.debug(f"Loaded {len(df)} bottles from dataset")
        return df
        
    except Exception as e:
        logger.error(f"Error loading bottle dataset: {str(e)}")
        
        # Create a fallback dataset with known bottles from Carrie's collection
        data = {
            'id': [13266, 16773, 2580, 24961, 6462],
            'name': ["Heaven Hill Bottled In Bond 7 Year", "Empress 1908 Indigo Gin", "J.P. Wiser's 18 Year", "Rare Perfection 14 Year", "Hendrick's Gin"],
            'spirit_type': ["Bourbon", "Gin", "Canadian Whisky", "Canadian Whisky", "Gin"],
            'abv': [50.0, 42.5, 40.0, 50.35, 44.0],
            'proof': [100.0, 85.0, 80.0, 100.7, 88.0], 
            'msrp': [47.74, 39.97, 61.87, 160.0, 37.97],
            'region': ["America", "Unknown", "Canada", "Canada", "Unknown"],
            'flavor_profile_vanilla': [70, 0, 0, 0, 0],
            'flavor_profile_caramel': [60, 0, 0, 0, 0],
            'flavor_profile_fruity': [0, 0, 0, 0, 0],
            'flavor_profile_spicy': [30, 0, 0, 0, 0],
            'flavor_profile_smoky': [0, 0, 0, 0, 0],
            'flavor_profile_peated': [0, 0, 0, 0, 0],
            'flavor_profile_sherried': [0, 0, 0, 0, 0]
        }
        
        df = pd.DataFrame(data)
        logger.debug(f"Using fallback dataset with {len(df)} bottles")
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