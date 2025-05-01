# Currently unused, but could be expanded if database persistence is needed
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Bottle:
    """Represents a whisky bottle with all its attributes"""
    id: str
    name: str
    size: str = None
    proof: float = None
    abv: float = None
    spirit_type: str = None
    brand_id: str = None
    region: str = None
    popularity: float = None
    image_url: str = None
    msrp: float = None
    fair_price: float = None
    shelf_price: float = None
    total_score: float = None
    wishlist_count: int = None
    vote_count: int = None
    bar_count: int = None
    ranking: int = None
    flavor_profile: Dict[str, float] = None
    tasting_notes: List[str] = None

@dataclass
class UserPreferences:
    """Represents a user's whisky preferences extracted from their collection"""
    preferred_regions: Dict[str, float] = None
    flavor_profiles: Dict[str, float] = None
    price_ranges: Dict[str, float] = None
    age_statements: Dict[str, float] = None
    spirit_types: Dict[str, float] = None
    brand_preferences: Dict[str, float] = None
    abv_preferences: Dict[str, float] = None
    average_bottle_price: float = None
    price_ceiling: float = None
    collection_size: int = None
