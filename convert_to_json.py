import json
import pandas as pd
import io

# Load the TSV data
with open('attached_assets/Pasted-id-name-size-proof-abv-spirit-type-brand-id-popularity-image-url-avg-msrp-fair-price-shelf-price-tot-1746093444201.txt', 'r') as f:
    data = f.read()

# Parse TSV data
df = pd.read_csv(io.StringIO(data), sep='\t')

# Convert numeric columns to appropriate types
numeric_cols = ['id', 'size', 'proof', 'abv', 'brand_id', 'popularity', 
                'avg_msrp', 'fair_price', 'shelf_price', 'total_score', 'wishlist_count']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill NaN values in proof/abv columns based on each other
df['proof'].fillna(df['abv'] * 2, inplace=True)
df['abv'].fillna(df['proof'] / 2, inplace=True)

# Create region field based on spirit_type
df['region'] = 'Unknown'
df.loc[df['spirit_type'] == 'Bourbon', 'region'] = 'America'
df.loc[df['spirit_type'] == 'Rye', 'region'] = 'America'
df.loc[df['spirit_type'].str.contains('Scotch', na=False), 'region'] = 'Scotland'
df.loc[df['spirit_type'] == 'Japanese Whisky', 'region'] = 'Japan'
df.loc[df['spirit_type'] == 'Irish Whiskey', 'region'] = 'Ireland'
df.loc[df['spirit_type'] == 'Canadian Whisky', 'region'] = 'Canada'

# Add basic flavor profiles based on spirit_type
df['flavor_profile'] = None
for idx, row in df.iterrows():
    flavor_profile = {}
    spirit = row['spirit_type']
    proof = row['proof'] if not pd.isna(row['proof']) else 0
    
    # Default values
    flavor_profile = {
        'vanilla': 0,
        'caramel': 0,
        'fruity': 0,
        'spicy': 0,
        'smoky': 0,
        'peated': 0,
        'sherried': 0,
    }
    
    # Bourbon tends to have vanilla, caramel notes
    if spirit == 'Bourbon':
        flavor_profile['vanilla'] = 70
        flavor_profile['caramel'] = 60
        flavor_profile['spicy'] = 30
    
    # Rye is typically spicier
    elif spirit == 'Rye':
        flavor_profile['spicy'] = 80
        flavor_profile['fruity'] = 20
    
    # Scotch can be peated/smoky
    elif 'Scotch' in str(spirit):
        flavor_profile['peated'] = 40
        flavor_profile['smoky'] = 30
        flavor_profile['sherried'] = 25
    
    # Higher proof tends to have more intense flavors
    if proof > 100:
        flavor_profile['spicy'] += 15
    
    df.at[idx, 'flavor_profile'] = flavor_profile

# Convert to list of dictionaries for JSON
bottles = df.to_dict('records')

# Write to JSON file
with open('static/data/bottles.json', 'w') as f:
    json.dump(bottles, f, indent=2)

print(f"Successfully converted {len(bottles)} bottles to JSON format")