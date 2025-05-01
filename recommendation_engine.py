import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from bottle_dataset import get_bottle_dataset

logger = logging.getLogger(__name__)

def analyze_preferences(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a user's whisky preferences based on their bar collection.
    
    Args:
        user_data: Dictionary containing the user's bar data from BAXUS API
        
    Returns:
        Dictionary of user preferences including regions, flavor profiles, etc.
    """
    preferences = {
        'preferred_regions': {},
        'spirit_types': {},
        'flavor_profiles': {
            'peated': 0,
            'sherried': 0,
            'fruity': 0,
            'spicy': 0,
            'smoky': 0,
            'vanilla': 0,
            'caramel': 0
        },
        'price_ranges': {
            'entry': 0,  # $0-50
            'mid': 0,    # $51-100
            'premium': 0,  # $101-200
            'luxury': 0   # $201+
        },
        'brand_preferences': {},
        'abv_preferences': {
            'low': 0,    # <43%
            'medium': 0, # 43-50%
            'high': 0    # >50%
        },
        'average_bottle_price': 0,
        'price_ceiling': 0,
        'collection_size': 0
    }
    
    # Extract collection data
    if 'bar' not in user_data or not user_data['bar']:
        logger.warning("No bar data found in user data")
        return preferences
    
    collection = user_data['bar']
    preferences['collection_size'] = len(collection)
    
    if preferences['collection_size'] == 0:
        return preferences
    
    # Process each bottle in the collection
    total_price = 0
    price_ceiling = 0
    
    logger.debug(f"Processing {len(collection)} bottles from user's collection")
    
    for bottle in collection:
        # Each item in the collection has a 'product' field with bottle details
        product = bottle.get('product')
        if not product:
            logger.debug("No product information found in bottle entry")
            continue
        
        # Extract relevant information from the product
        product_id = product.get('id')
        if not product_id:
            logger.debug("No product ID found")
            continue
        
        # Extract spirit type (e.g., Bourbon, Single Malt, etc.)
        spirit_type = product.get('spirit')
        if spirit_type:
            preferences['spirit_types'][spirit_type] = preferences['spirit_types'].get(spirit_type, 0) + 1
        
        # Extract region based on spirit type
        region = None
        if "Scotch" in str(spirit_type):
            region = "Scotland"
        elif spirit_type == "Bourbon" or spirit_type == "Rye":
            region = "America"
        elif spirit_type == "Japanese Whisky":
            region = "Japan"
        elif spirit_type == "Irish Whiskey":
            region = "Ireland"
        elif spirit_type == "Canadian Whisky":
            region = "Canada"
        
        if region:
            preferences['preferred_regions'][region] = preferences['preferred_regions'].get(region, 0) + 1
        
        # Update price range preferences based on average_msrp
        price = product.get('average_msrp', 0)
        if price:
            total_price += price
            price_ceiling = max(price_ceiling, price)
            
            if price <= 50:
                preferences['price_ranges']['entry'] += 1
            elif price <= 100:
                preferences['price_ranges']['mid'] += 1
            elif price <= 200:
                preferences['price_ranges']['premium'] += 1
            else:
                preferences['price_ranges']['luxury'] += 1
        
        # Update brand preferences
        brand = product.get('brand')
        if brand:
            preferences['brand_preferences'][brand] = preferences['brand_preferences'].get(brand, 0) + 1
        
        # Update ABV preferences based on proof
        proof = product.get('proof', 0)
        if proof:
            abv = proof / 2  # Convert proof to ABV
            if abv < 43:
                preferences['abv_preferences']['low'] += 1
            elif abv <= 50:
                preferences['abv_preferences']['medium'] += 1
            else:
                preferences['abv_preferences']['high'] += 1
                
        # For flavor profiles, derive from spirit types since real flavor data is not in API
        # This is a simplified approach - in a real implementation we'd use machine learning or a database
        if spirit_type == "Bourbon":
            preferences['flavor_profiles']['vanilla'] += 60
            preferences['flavor_profiles']['caramel'] += 70
            preferences['flavor_profiles']['spicy'] += 40
        elif "Scotch" in str(spirit_type):
            preferences['flavor_profiles']['peated'] += 40
            preferences['flavor_profiles']['smoky'] += 30
        elif spirit_type == "Rye":
            preferences['flavor_profiles']['spicy'] += 80
        elif spirit_type == "Gin":
            preferences['flavor_profiles']['fruity'] += 50
    
    # Calculate average bottle price
    if preferences['collection_size'] > 0:
        preferences['average_bottle_price'] = total_price / preferences['collection_size']
    
    # Set price ceiling (with 20% buffer for recommendations)
    preferences['price_ceiling'] = price_ceiling * 1.2
    
    # Normalize flavor profiles to an average per bottle
    for flavor in preferences['flavor_profiles'].keys():
        preferences['flavor_profiles'][flavor] /= max(preferences['collection_size'], 1)
    
    # Convert counts to percentages for categorical preferences
    for category in ['preferred_regions', 'spirit_types', 'price_ranges', 'brand_preferences', 'abv_preferences']:
        total = sum(preferences[category].values())
        if total > 0:
            for key in preferences[category]:
                preferences[category][key] = (preferences[category][key] / total) * 100
    
    return preferences

def generate_recommendations(preferences: Dict[str, Any], user_data: Dict[str, Any], 
                            num_recommendations: int = 5) -> List[Dict[str, Any]]:
    """
    Generates personalized bottle recommendations based on user preferences.
    
    Args:
        preferences: Dictionary of analyzed user preferences
        user_data: Original user data from BAXUS API
        num_recommendations: Number of recommendations to generate
        
    Returns:
        List of recommended bottles with detailed information
    """
    # Get the bottle dataset
    bottle_df = get_bottle_dataset()
    
    # Extract user's collection IDs to avoid recommending bottles they already have
    collection_ids = []
    if 'bar' in user_data and user_data['bar']:
        collection_ids = [bottle.get('release_id') for bottle in user_data['bar'] if bottle.get('release_id')]
    
    logger.debug(f"Found {len(collection_ids)} bottles in user collection: {collection_ids[:5]}...")
    
    # Remove bottles already in the user's collection
    candidate_bottles = bottle_df[~bottle_df['id'].isin(collection_ids)].copy()
    
    if candidate_bottles.empty:
        logger.warning("No candidate bottles available for recommendation")
        return []
    
    # Price filter: Don't recommend bottles much more expensive than user's price ceiling
    price_ceiling = preferences.get('price_ceiling', float('inf'))
    price_floor = max(0, preferences.get('average_bottle_price', 0) * 0.5)
    candidate_bottles = candidate_bottles[(candidate_bottles['msrp'] <= price_ceiling) & 
                                         (candidate_bottles['msrp'] >= price_floor)]
    
    if candidate_bottles.empty:
        logger.warning("No bottles in appropriate price range")
        return []
    
    # Prepare feature matrix for recommendation
    feature_columns = [
        'abv', 'msrp',
        'flavor_profile_peated', 'flavor_profile_sherried', 
        'flavor_profile_fruity', 'flavor_profile_spicy',
        'flavor_profile_smoky', 'flavor_profile_vanilla', 'flavor_profile_caramel'
    ]
    
    # One-hot encode categorical features
    candidate_bottles_encoded = pd.get_dummies(
        candidate_bottles, 
        columns=['spirit_type', 'region'],
        prefix=['spirit', 'region']
    )
    
    # Add the one-hot encoded columns to our feature list
    encoded_features = [col for col in candidate_bottles_encoded.columns 
                       if col.startswith('spirit_') or col.startswith('region_')]
    feature_columns.extend(encoded_features)
    
    # Ensure all feature columns exist in the dataframe
    feature_columns = [col for col in feature_columns if col in candidate_bottles_encoded.columns]
    
    # Create feature matrix
    X = candidate_bottles_encoded[feature_columns].values
    
    # Normalize features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Create a user preference vector based on their collection
    user_vector = np.zeros(len(feature_columns))
    
    # Set numeric preferences
    for i, col in enumerate(feature_columns):
        if col == 'abv':
            # Calculate weighted average ABV preference
            abv_pref = preferences['abv_preferences']
            user_vector[i] = (
                (abv_pref.get('low', 0) * 40) + 
                (abv_pref.get('medium', 0) * 46) + 
                (abv_pref.get('high', 0) * 55)
            ) / 100
        elif col == 'msrp':
            user_vector[i] = preferences.get('average_bottle_price', 0)
        elif col.startswith('flavor_profile_'):
            flavor = col.replace('flavor_profile_', '')
            user_vector[i] = preferences['flavor_profiles'].get(flavor, 0)
        elif col.startswith('spirit_'):
            spirit = col.replace('spirit_', '')
            user_vector[i] = preferences['spirit_types'].get(spirit, 0) / 100
        elif col.startswith('region_'):
            region = col.replace('region_', '')
            user_vector[i] = preferences['preferred_regions'].get(region, 0) / 100
    
    # Scale user vector
    user_vector_scaled = scaler.transform(user_vector.reshape(1, -1))
    
    # Use k-nearest neighbors to find similar bottles
    knn = NearestNeighbors(n_neighbors=min(num_recommendations * 3, len(X_scaled)), 
                          algorithm='auto', metric='euclidean')
    knn.fit(X_scaled)
    
    distances, indices = knn.kneighbors(user_vector_scaled)
    
    # Get candidate recommendation indices
    candidate_indices = indices[0]
    
    # Prepare final recommendations with diversity
    recommendations = []
    recommended_regions = set()
    recommended_spirit_types = set()
    
    for idx in candidate_indices:
        bottle = candidate_bottles.iloc[idx].to_dict()
        
        # Ensure diversity by avoiding too many of the same region or spirit type
        region = bottle.get('region')
        spirit_type = bottle.get('spirit_type')
        
        # Skip if we already have two bottles of this region or spirit type
        if (region in recommended_regions and len([r for r in recommendations if r.get('region') == region]) >= 2) or \
           (spirit_type in recommended_spirit_types and len([r for r in recommendations if r.get('spirit_type') == spirit_type]) >= 2):
            continue
        
        # Add region and spirit type to tracking sets
        recommended_regions.add(region)
        recommended_spirit_types.add(spirit_type)
        
        # Generate explanation for this recommendation
        explanation = generate_recommendation_explanation(bottle, preferences, user_data)
        bottle['explanation'] = explanation
        
        recommendations.append(bottle)
        
        # Stop once we have enough recommendations
        if len(recommendations) >= num_recommendations:
            break
    
    # If we don't have enough recommendations, add more
    if len(recommendations) < num_recommendations:
        for idx in candidate_indices:
            bottle = candidate_bottles.iloc[idx].to_dict()
            if any(r.get('id') == bottle.get('id') for r in recommendations):
                continue
            
            explanation = generate_recommendation_explanation(bottle, preferences, user_data)
            bottle['explanation'] = explanation
            
            recommendations.append(bottle)
            
            if len(recommendations) >= num_recommendations:
                break
    
    return recommendations

def generate_recommendation_explanation(bottle: Dict[str, Any], 
                                       preferences: Dict[str, Any],
                                       user_data: Dict[str, Any]) -> str:
    """
    Generates a personalized explanation for why a bottle is recommended.
    
    Args:
        bottle: Dictionary containing bottle information from our dataset
        preferences: Dictionary of user preferences
        user_data: Original user data from BAXUS API
        
    Returns:
        String containing personalized explanation
    """
    explanation_parts = []
    
    # Region-based explanation
    region = bottle.get('region')
    region_pref = preferences.get('preferred_regions', {})
    if region and region in region_pref and region_pref[region] > 20:
        explanation_parts.append(f"This {region} whisky aligns with your preference for bottles from this region.")
    elif region:
        # Find example bottle from user's collection with same region
        similar_region_bottle = None
        for user_bottle in user_data.get('bar', []):
            product = user_bottle.get('product')
            if product:
                # Determine region of user's bottle based on spirit type
                user_region = None
                spirit = product.get('spirit')
                if spirit:
                    if "Scotch" in str(spirit):
                        user_region = "Scotland"
                    elif spirit == "Bourbon" or spirit == "Rye":
                        user_region = "America"
                    elif spirit == "Japanese Whisky":
                        user_region = "Japan"
                    elif spirit == "Irish Whiskey":
                        user_region = "Ireland"
                    elif spirit == "Canadian Whisky":
                        user_region = "Canada"
                    
                    if user_region == region:
                        similar_region_bottle = product.get('name')
                        break
        
        if similar_region_bottle:
            explanation_parts.append(f"Like your {similar_region_bottle}, this is also from {region}.")
        elif region not in region_pref or region_pref[region] < 10:
            explanation_parts.append(f"This would add diversity to your collection with a {region} whisky.")
    
    # Spirit type explanation
    spirit_type = bottle.get('spirit_type')
    spirit_pref = preferences.get('spirit_types', {})
    if spirit_type and spirit_type in spirit_pref and spirit_pref[spirit_type] > 20:
        explanation_parts.append(f"This {spirit_type} matches your preferred style.")
    elif spirit_type and (spirit_type not in spirit_pref or spirit_pref[spirit_type] < 10):
        explanation_parts.append(f"This {spirit_type} would add variety to your collection.")
    
    # Flavor profile explanation
    flavor_prefs = preferences.get('flavor_profiles', {})
    bottle_flavors = {}
    for key, value in bottle.items():
        if key.startswith('flavor_profile_'):
            flavor = key.replace('flavor_profile_', '')
            bottle_flavors[flavor] = value
    
    # Find dominant flavors in the bottle and user preferences
    dominant_bottle_flavors = sorted(bottle_flavors.items(), key=lambda x: x[1], reverse=True)[:2]
    dominant_user_flavors = sorted(flavor_prefs.items(), key=lambda x: x[1], reverse=True)[:2]
    
    flavor_matches = [flavor for flavor, _ in dominant_bottle_flavors 
                     if flavor in dict(dominant_user_flavors)]
    
    if flavor_matches:
        flavor_text = ", ".join(flavor_matches)
        explanation_parts.append(f"The {flavor_text} notes in this whisky match your flavor preferences.")
    else:
        complementary_flavor = dominant_bottle_flavors[0][0] if dominant_bottle_flavors else None
        if complementary_flavor:
            explanation_parts.append(f"This whisky's {complementary_flavor} character would complement your collection.")
    
    # Price explanation
    price = bottle.get('msrp', 0)
    avg_price = preferences.get('average_bottle_price', 0)
    if avg_price > 0:
        if price <= avg_price * 0.8:
            explanation_parts.append(f"At ${price:.2f}, this is a good value compared to your collection average.")
        elif price <= avg_price * 1.2:
            explanation_parts.append(f"This is priced similarly to most bottles in your collection.")
        else:
            explanation_parts.append(f"This premium offering is slightly above your usual price range but worth considering.")
    else:
        explanation_parts.append(f"At ${price:.2f}, this is a bottle worth considering for your collection.")
    
    # Rating/score explanation
    score = bottle.get('total_score', 0)
    if score > 90:
        explanation_parts.append("This highly-rated whisky is widely regarded as exceptional.")
    elif score > 85:
        explanation_parts.append("This well-rated whisky offers excellent quality.")
    elif score > 80:
        explanation_parts.append("This solid whisky has positive ratings overall.")
    
    # Combine all explanations
    explanation = " ".join(explanation_parts)
    
    if not explanation:
        explanation = "This bottle would make a nice addition to your whisky collection."
    
    return explanation
