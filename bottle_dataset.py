import pandas as pd
import logging
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# JSON dataset of bottles
BOTTLE_DATA = [
    {
        "id": 13266,
        "name": "Heaven Hill Bottled In Bond 7 Year",
        "size": 750,
        "proof": 100.0,
        "abv": 50.0,
        "spirit_type": "Bourbon",
        "brand_id": 430,
        "popularity": 100144,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recSJfTSxTvljLvF8",
        "msrp": 47.74,
        "fair_price": 62.34,
        "shelf_price": 84.99,
        "total_score": 18850,
        "wishlist_count": 1948
    },
    {
        "id": 16773,
        "name": "Empress 1908 Indigo Gin",
        "size": 750,
        "proof": 85.0,
        "abv": 42.5,
        "spirit_type": "Gin",
        "brand_id": 3101,
        "popularity": 7,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/b67b57e0-548c-430d-982f-d9c68f3d17f4",
        "msrp": 39.97,
        "fair_price": 51.47,
        "shelf_price": 43.19,
        "total_score": 6541,
        "wishlist_count": 307
    },
    {
        "id": 2580,
        "name": "J.P. Wiser's 18 Year",
        "size": 750,
        "proof": 80.0,
        "abv": 40.0,
        "spirit_type": "Canadian Whisky",
        "brand_id": 159,
        "popularity": 2,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec03I5wSqGi19rXR",
        "msrp": 61.87,
        "fair_price": 65.61,
        "shelf_price": 68.04,
        "total_score": 5427,
        "wishlist_count": 201
    },
    {
        "id": 24961,
        "name": "Rare Perfection 14 Year",
        "size": 750,
        "proof": 100.7,
        "abv": 50.35,
        "spirit_type": "Canadian Whisky",
        "brand_id": 2827,
        "popularity": 0,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/247ad792-6d80-4d4d-92f6-4789183cd2f0",
        "msrp": 160.0,
        "fair_price": 164.85,
        "shelf_price": 179.39,
        "total_score": 3210,
        "wishlist_count": 88
    },
    {
        "id": 6462,
        "name": "Hendrick's Gin",
        "size": 750,
        "proof": 88.0,
        "abv": 44.0,
        "spirit_type": "Gin",
        "brand_id": 1074,
        "popularity": 933,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recvWBDL5jDagd2Dw",
        "msrp": 37.97,
        "fair_price": 40.56,
        "shelf_price": 39.13,
        "total_score": 7542,
        "wishlist_count": 941
    },
    {
        "id": 164,
        "name": "Blanton's Original Single Barrel",
        "size": 750,
        "proof": 93.0,
        "abv": 46.5,
        "spirit_type": "Bourbon",
        "brand_id": 10,
        "popularity": 100737,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec8QcHSZugg64kQy",
        "msrp": 74.99,
        "fair_price": 104.52,
        "shelf_price": 139.86,
        "total_score": 92451,
        "wishlist_count": 8983
    },
    {
        "id": 2848,
        "name": "Eagle Rare 10 Year",
        "size": 750,
        "proof": 90.0,
        "abv": 45.0,
        "spirit_type": "Bourbon",
        "brand_id": 542,
        "popularity": 100519,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/ecce066b-6b3d-4b58-bd04-8bf9c67e3e92",
        "msrp": 39.99,
        "fair_price": 66.25,
        "shelf_price": 49.99,
        "total_score": 82217,
        "wishlist_count": 8744
    },
    {
        "id": 4984,
        "name": "E.H. Taylor, Jr. Small Batch",
        "size": 750,
        "proof": 100.0,
        "abv": 50.0,
        "spirit_type": "Bourbon",
        "brand_id": 210,
        "popularity": 100407,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recE8VJ2hGGJwZjdh",
        "msrp": 44.99,
        "fair_price": 94.43,
        "shelf_price": 93.57,
        "total_score": 61777,
        "wishlist_count": 8161
    },
    {
        "id": 466,
        "name": "Buffalo Trace",
        "size": 750,
        "proof": 90.0,
        "abv": 45.0,
        "spirit_type": "Bourbon",
        "brand_id": 245,
        "popularity": 100447,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recbYY28UjL8EfuFD",
        "msrp": 26.99,
        "fair_price": 41.82,
        "shelf_price": 36.96,
        "total_score": 49610,
        "wishlist_count": 3403
    },
    {
        "id": 158,
        "name": "Weller Antique 107",
        "size": 750,
        "proof": 107.0,
        "abv": 53.5,
        "spirit_type": "Bourbon",
        "brand_id": 156,
        "popularity": 100266,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec8X36afthvgqzO9",
        "msrp": 56.35,
        "fair_price": 116.66,
        "shelf_price": 109.89,
        "total_score": 40001,
        "wishlist_count": 8098
    },
    {
        "id": 1805,
        "name": "Sazerac Rye Whiskey",
        "size": 750,
        "proof": 90.0,
        "abv": 45.0,
        "spirit_type": "Rye",
        "brand_id": 705,
        "popularity": 100054,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recRzB6sPjEkkc9Ac",
        "msrp": 28.73,
        "fair_price": 46.77,
        "shelf_price": 51.89,
        "total_score": 13399,
        "wishlist_count": 776
    },
    {
        "id": 1282,
        "name": "Willett Family Estate Small Batch Rye 4 Year",
        "size": 750,
        "proof": 110.0,
        "abv": 55.0,
        "spirit_type": "Rye",
        "brand_id": 2986,
        "popularity": 100049,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/89de97f2-13d3-400f-9731-bdc4bf3034a3",
        "msrp": 60.58,
        "fair_price": 89.01,
        "shelf_price": 93.69,
        "total_score": 7534,
        "wishlist_count": 595
    },
    {
        "id": 1296,
        "name": "Knob Creek 12 Year",
        "size": 750,
        "proof": 100.0,
        "abv": 50.0,
        "spirit_type": "Bourbon",
        "brand_id": 189,
        "popularity": 100113,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/recLpshU8Flh0HWX2",
        "msrp": 61.99,
        "fair_price": 86.81,
        "shelf_price": 91.29,
        "total_score": 13625,
        "wishlist_count": 1444
    },
    {
        "id": 263,
        "name": "Old Forester 1920 Prohibition Style",
        "size": 750,
        "proof": 115.0,
        "abv": 57.5,
        "spirit_type": "Bourbon",
        "brand_id": 152,
        "popularity": 100076,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec9rWFMe841rV5IM",
        "msrp": 59.33,
        "fair_price": 72.85,
        "shelf_price": 67.99,
        "total_score": 11816,
        "wishlist_count": 1919
    },
    {
        "id": 2993,
        "name": "Stagg Jr.",
        "size": 750,
        "proof": 134.4,
        "abv": 67.2,
        "spirit_type": "Bourbon",
        "brand_id": 3640,
        "popularity": 100027,
        "image_url": "https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec5jaoF5vloYmUBL",
        "msrp": 49.46,
        "fair_price": 147.92,
        "shelf_price": 172.99,
        "total_score": 23209,
        "wishlist_count": 6685
    }
]

def get_bottle_dataset() -> pd.DataFrame:
    """
    Loads the bottle dataset from our JSON data
    
    Returns:
        A pandas DataFrame containing all bottles with their attributes
    """
    # Create DataFrame from our JSON data
    df = pd.DataFrame(BOTTLE_DATA)
    
    logger.debug(f"Loaded {len(df)} bottles from JSON dataset")
    
    # Add region based on spirit_type
    df['region'] = 'Unknown'
    df.loc[df['spirit_type'] == 'Bourbon', 'region'] = 'America'
    df.loc[df['spirit_type'] == 'Rye', 'region'] = 'America'
    df.loc[df['spirit_type'].str.contains('Scotch', na=False), 'region'] = 'Scotland'
    df.loc[df['spirit_type'] == 'Japanese Whisky', 'region'] = 'Japan'
    df.loc[df['spirit_type'] == 'Irish Whiskey', 'region'] = 'Ireland'
    df.loc[df['spirit_type'] == 'Canadian Whisky', 'region'] = 'Canada'
    
    # Add flavor profiles based on spirit_type and other attributes
    # These are approximations for the demo
    df['flavor_profile_peated'] = 0
    df['flavor_profile_sherried'] = 0
    df['flavor_profile_fruity'] = 0
    df['flavor_profile_spicy'] = 0
    df['flavor_profile_smoky'] = 0
    df['flavor_profile_vanilla'] = 0
    df['flavor_profile_caramel'] = 0
    
    # Bourbon tends to have vanilla, caramel and sometimes spicy notes
    bourbon_mask = df['spirit_type'] == 'Bourbon'
    df.loc[bourbon_mask, 'flavor_profile_vanilla'] = 70
    df.loc[bourbon_mask, 'flavor_profile_caramel'] = 60
    df.loc[bourbon_mask, 'flavor_profile_spicy'] = 30
    
    # Rye is typically spicier
    rye_mask = df['spirit_type'] == 'Rye'
    df.loc[rye_mask, 'flavor_profile_spicy'] = 80
    df.loc[rye_mask, 'flavor_profile_fruity'] = 20
    
    # Scotch can be peated/smoky depending on region
    scotch_mask = df['spirit_type'].str.contains('Scotch', na=False)
    df.loc[scotch_mask, 'flavor_profile_peated'] = 40
    df.loc[scotch_mask, 'flavor_profile_smoky'] = 30
    df.loc[scotch_mask, 'flavor_profile_sherried'] = 25
    
    # Higher proof tends to have more intense flavors
    high_proof_mask = df['proof'] > 100
    df.loc[high_proof_mask, 'flavor_profile_spicy'] += 15
    
    # Convert to categorical types for efficiency
    df['spirit_type'] = pd.Categorical(df['spirit_type'])
    df['region'] = pd.Categorical(df['region'])
    
    logger.debug(f"Loaded {len(df)} bottles from dataset")
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
