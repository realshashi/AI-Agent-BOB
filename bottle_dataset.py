import pandas as pd
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_bottle_dataset() -> pd.DataFrame:
    """
    Loads the real whisky bottle dataset.
    
    Returns:
        A pandas DataFrame containing all bottles with their attributes
    """
    # Try to load the real dataset from multiple possible locations
    possible_paths = [
        'attached_assets/dataset.csv',
        'static/data/dataset.csv'
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
            
    if not dataset_path:
        logger.warning(f"Dataset file not found in any of the expected locations, using fallback data")
        return _get_fallback_dataset()  # Use fallback if file not found
    
    try:
        # Read the CSV file
        df = pd.read_csv(dataset_path)
        logger.info(f"Loaded real dataset with {len(df)} bottles")
        
        # Convert column names to match our expected format
        column_mapping = {
            'avg_msrp': 'msrp',
            'abv': 'abv',
            'spirit_type': 'spirit_type',
            'total_score': 'total_score'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and old_name != new_name:
                df = df.rename(columns={old_name: new_name})
        
        # Fill missing values
        df['abv'] = df['abv'].fillna(df['proof'] / 2 if 'proof' in df.columns else 45)
        df['msrp'] = df['msrp'].fillna(50)  # Default price if missing
        
        # Add region info based on spirit type if missing
        if 'region' not in df.columns:
            df['region'] = df['spirit_type'].apply(_derive_region)
        
        # Add flavor profiles - in a real system this would come from a flavor database
        # Here we're inferring based on spirit type
        df['flavor_profile_peated'] = df['spirit_type'].apply(lambda x: 80 if 'Scotch' in str(x) else 20)
        df['flavor_profile_sherried'] = df['spirit_type'].apply(lambda x: 70 if 'Scotch' in str(x) else 30)
        df['flavor_profile_fruity'] = df['spirit_type'].apply(lambda x: 60 if 'Rye' in str(x) else 40)
        df['flavor_profile_spicy'] = df['spirit_type'].apply(lambda x: 75 if 'Rye' in str(x) else 30)
        df['flavor_profile_smoky'] = df['flavor_profile_peated'] * 0.8
        df['flavor_profile_vanilla'] = df['spirit_type'].apply(lambda x: 80 if 'Bourbon' in str(x) else 40)
        df['flavor_profile_caramel'] = df['spirit_type'].apply(lambda x: 70 if 'Bourbon' in str(x) else 30)
        
        # Convert to categorical types for efficiency
        if 'spirit_type' in df.columns:
            df['spirit_type'] = pd.Categorical(df['spirit_type'])
        if 'region' in df.columns:
            df['region'] = pd.Categorical(df['region'])
        
        return df
    except Exception as e:
        logger.exception(f"Error loading real dataset: {str(e)}")
        return _get_fallback_dataset()  # Use fallback if there's an error

def _derive_region(spirit_type: str) -> str:
    """Helper to derive region from spirit type"""
    spirit_type = str(spirit_type).lower()
    if 'scotch' in spirit_type or 'scotland' in spirit_type:
        if 'islay' in spirit_type:
            return 'Scotland-Islay'
        elif 'speyside' in spirit_type:
            return 'Scotland-Speyside'
        elif 'highland' in spirit_type:
            return 'Scotland-Highland'
        return 'Scotland'
    elif 'bourbon' in spirit_type or 'rye' in spirit_type or 'tennessee' in spirit_type:
        return 'America'
    elif 'japanese' in spirit_type or 'japan' in spirit_type:
        return 'Japan'
    elif 'irish' in spirit_type or 'ireland' in spirit_type:
        return 'Ireland'
    elif 'canadian' in spirit_type or 'canada' in spirit_type:
        return 'Canada'
    else:
        return 'Other'

def _get_fallback_dataset() -> pd.DataFrame:
    """
    Creates a fallback dataset when the real one can't be loaded.
    """
    logger.warning("Using fallback bottle dataset")
    # Create a simplified mock dataset structure
    data = {
        'id': list(range(1, 101)),
        'name': [f"Whisky {i}" for i in range(1, 101)],
        'spirit_type': ['Single Malt', 'Bourbon', 'Rye', 'Blended Scotch', 'Japanese'] * 20,
        'region': ['Scotland-Islay', 'Scotland-Speyside', 'America', 'Japan', 'Ireland'] * 20,
        'abv': [40 + (i % 20) for i in range(1, 101)],
        'msrp': [50 + (i % 200) for i in range(1, 101)],
        'fair_price': [60 + (i % 250) for i in range(1, 101)],
        'total_score': [80 + (i % 20) for i in range(1, 101)],
        'flavor_profile_peated': [(i % 5) * 20 for i in range(1, 101)],
        'flavor_profile_sherried': [(i % 4) * 25 for i in range(1, 101)],
        'flavor_profile_fruity': [(i % 3) * 30 for i in range(1, 101)],
        'flavor_profile_spicy': [(i % 6) * 15 for i in range(1, 101)],
        'brand_id': [f"Brand-{(i % 50) + 1}" for i in range(1, 101)],
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
