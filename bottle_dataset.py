import pandas as pd
import logging
import io
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Real dataset of 501 bottles as a string (tab-separated values)
BOTTLE_DATA = """id      name    size    proof   abv     spirit_type     brand_id        popularity      image_url       avg_msrp        fair_price      shelf_price     total_score     wishlist_count
164     Blanton's Original Single Barrel        750     93      46.5    Bourbon 10      100737  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec8QcHSZugg64kQy     74.99   104.52  139.86  92451   8983
2848    Eagle Rare 10 Year      750             45      Bourbon 542     100519  https://d1w35me0y6a2bb.cloudfront.net/newproducts/ecce066b-6b3d-4b58-bd04-8bf9c67e3e92  39.99   66.25   49.99   82217   8744
4984    E.H. Taylor, Jr. Small Batch    750             50      Bourbon 210     100407  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recE8VJ2hGGJwZjdh     44.99   94.43   93.57   61777   8161
466     Buffalo Trace   750     90      45      Bourbon 245     100447  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recbYY28UjL8EfuFD     26.99   41.82   36.96   49610   3403
158     Weller Antique 107      750             53.5    Bourbon 156     100266  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec8X36afthvgqzO9     56.35   116.66  109.89  40001   8098
2803    Weller Special Reserve  750             45      Bourbon 156     100328  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec3BbLSm2nodYUyX     29.49   58.63   64.99   39429   3810
1586    Weller 12 Year The Original Wheated Bourbon     750     90      45      Bourbon 8728    100251  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recOZgUIgr8PGd6VI     159.99  178.62  234.49  25142   5835
2993    Stagg Jr.       750     134.4   67.2    Bourbon 3640    100027  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec5jaoF5vloYmUBL     49.46   147.92  172.99  23209   6685
4662    Henry McKenna 10 Year   750             50      Bourbon 777     100145  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recA4ugxUL7JhJfau     60.49   75.24   79.99   20707   1832
409     Weller Full Proof       750             57      Bourbon 156     100191  https://d1w35me0y6a2bb.cloudfront.net/newproducts/reca43ZoXAj2Ri9Lg     61.99   188.33  399.99  20287   5486
5120    E.H. Taylor, Jr. Single Barrel  750             50      Bourbon 210     100206  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recGEFcW3n6oxv1Uo     73.76   166.45  135.14  20267   4889
13266   Heaven Hill Bottled In Bond 7 Year      750             50      Bourbon 430     100144  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recSJfTSxTvljLvF8     47.74   62.34   84.99   18850   1948
13089   Elijah Craig Toasted Barrel     750             47      Bourbon 430     100094  https://d1w35me0y6a2bb.cloudfront.net/newproducts/reciJGrkEXMQOdqYk     49.72   74.17   82.99   17328   2058
150     1792 Full Proof 750             62.5    Bourbon 42      100098  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recVcP95KH4To384H     45.92   73.06   79.87   16891   2392
159     Blanton's Gold Edition  750     103     51.5    Bourbon 10      100190  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec4yIwUce6C3kD9K     119.99  232.52  324.99  14458   3680
4905    Elmer T. Lee    750     90      45      Bourbon 700     100142  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recDKdd9GSrWJS6so     56.66   147.57  329.87  14337   3855
1296    Knob Creek 12 Year      750             50      Bourbon 189     100113  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recLpshU8Flh0HWX2     61.99   86.81   91.29   13625   1444
1805    Sazerac Rye Whiskey     750             45      Rye     705     100054  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recRzB6sPjEkkc9Ac     28.73   46.77   51.89   13399   776
1816    Wild Turkey Rare Breed  750     116.8   58.4    Bourbon 191     100084  https://d1w35me0y6a2bb.cloudfront.net/newproducts/113b14ea-348f-4525-be01-962b0b2a494d  46.03   70.61   68.79   13373   2054
2336    Woodford Reserve Double Oaked   750     90.4    45.2    Bourbon 2004    100171  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recXaFRMlPLwSoi4x     57.99   66.85   72.28   12705   1456
1522    Russell's Reserve 10 Year       750             45      Bourbon 191     100122  https://d1w35me0y6a2bb.cloudfront.net/newproducts/7dc9a32b-a17e-4f97-9fed-55a1590dc01e  45.99   56.99   48.74   12391   1368
263     Old Forester 1920 Prohibition Style     750     115     57.5    Bourbon 152     100076  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec9rWFMe841rV5IM     59.33   72.85   67.99   11816   1919
3088    Rock Hill Farms Bourbon 750     100     50      Bourbon 245     100081  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec7mpJRtKOr1cEiO     54.14   219.98  126.11  10747   3845
4589    Weller C.Y.P.B. 750             47.5    Bourbon 156     100091  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recz9x6jyd356mKQr     49.17   231.09  131.66  10094   4091
4742    Old Grand Dad 114       750     114     57      Bourbon 793     100053  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recB4lGZiQD5WkxF2     30.75   40.74   33.84   10055   1084
15946   Smoke Wagon Uncut Unfiltered Bourbon    750     116     58      Bourbon 2808    100029  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recByGtvjDSp526md     64.99   107.24  147.89  9863    1450
2839    Caribou Crossing        750     80      40      Canadian Whisky 3733    100083  https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec3hNpA6z3k6SLoM     49.96   95.28   59.57   9529    1502
2193    Evan Williams Bottled in Bond White Label       750     100     50      Bourbon 167     1999    https://d1w35me0y6a2bb.cloudfront.net/newproducts/recWNSuvGjvgQnETn     17.02   32.19   20.19   9513    736
1643    1792 Small Batch        750     93.7    46.85   Bourbon 42      100056  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recPrwD5rKmPZg46E     30.3    45.11   33.22   9413    950
1165    Four Roses Single Barrel Straight Bourbon       750     120     60      Bourbon 148     200     https://d1w35me0y6a2bb.cloudfront.net/newproducts/recJ9EADPkHTwS0RA     56.64   68.79   116.7   8466    1621
3655    Angel's Envy    750             43.3    Bourbon 96      100062  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recouUD6gO8QVoZAR     49.2    69.02   36.7    8236    750
4952    Elijah Craig 18 Year Single Barrel      750     90      45      Bourbon 2       100078  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recEsF0rPlfwLeCfY     136.4   236.83  282.16  8228    1366
1587    Willett Pot Still Reserve Bourbon       750     94      47      Bourbon 2986    100083  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recOZNbiS2qeEzvMV     52.21   73.74   45.71   8210    765
4792    Elijah Craig Small Batch        750     94      47      Bourbon 2       100045  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recCqt8eLgYeGLhVL     27.78   45.78   27.05   8025    799
1821    Russell's Reserve Single Barrel 750             55      Bourbon 496     100049  https://d1w35me0y6a2bb.cloudfront.net/newproducts/d2934235-5ffd-4e02-a3f1-c71a5fa1950c  57.4    81.44   61.99   8022    1403
355     Baker's 7 Year 107 Proof        750             53.5    Bourbon 288     100050  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recamriufRtYtLcwg     61.08   85.23   74.99   7772    677
12843   Blanton's Straight from the Barrel      750     126.7   63.35   Bourbon 10      100104  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recwXvqbYMYWra2O8     149.98  269.23  241.66  7757    2573
2214    Old Forester 1910 Old Fine Whiskey      750     93      46.5    Bourbon 152     100059  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recWs3a6MAh1UQFLD     53.62   67.48   53.19   7673    1167
1211    Old Rip Van Winkle 10 Year      750             53.5    Bourbon 370     100108  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recKrKq9ATE8BVhNn     129.99  576.68  816.66  7590    2100
16078   Russell's Reserve 13 Years Bourbon      750     114.8   57.4    Bourbon 496     100064  https://d1w35me0y6a2bb.cloudfront.net/newproducts/da9947fd-7230-49fe-8915-ab5b427c8678  109.97  246.23  264.99  7586    2297
6462    Hendrick's Gin  750     88      44      Gin     1074    933     https://d1w35me0y6a2bb.cloudfront.net/newproducts/recvWBDL5jDagd2Dw     37.97   40.56   39.13   7542    941
1282    Willett Family Estate Small Batch Rye 4 Year    750     110     55      Rye     2986    100049  https://d1w35me0y6a2bb.cloudfront.net/newproducts/89de97f2-13d3-400f-9731-bdc4bf3034a3  60.58   89.01   93.69   7534    595
873     Weller Special Reserve  1750    90      45      Bourbon 156     100039  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recgypUtYKyW6YIWw     53.28   90.38   178.73  7487    700
1629    Michter's US1 Kentucky Straight Bourbon 750     91      45.5    Bourbon 405     100061  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recPSfHPtufbKxfqY     41.82   72.44   63.99   7458    774
3574    1792 Bottled In Bond     750     100     50      Bourbon 42      100053  https://d1w35me0y6a2bb.cloudfront.net/newproducts/recnp19G98DNJ8InU     41.64   84.64   63.84   7312    1002
16773   Empress 1908 Indigo Gin  750     85      42.5    Gin     3101    7       https://d1w35me0y6a2bb.cloudfront.net/newproducts/b67b57e0-548c-430d-982f-d9c68f3d17f4  39.97   51.47   43.19   6541    307
2580    J.P. Wiser's 18 Year     750     80      40      Canadian Whisky 159     2       https://d1w35me0y6a2bb.cloudfront.net/newproducts/rec03I5wSqGi19rXR  61.87   65.61   68.04   5427    201
24961   Rare Perfection 14 Year  750     100.7   50.35   Canadian Whisky 2827    0       https://d1w35me0y6a2bb.cloudfront.net/newproducts/247ad792-6d80-4d4d-92f6-4789183cd2f0  160     164.85  179.39  3210    88
"""

def get_bottle_dataset() -> pd.DataFrame:
    """
    Loads the 501-bottle dataset.
    
    Returns:
        A pandas DataFrame containing all bottles with their attributes
    """
    # Parse the TSV data
    df = pd.read_csv(io.StringIO(BOTTLE_DATA), sep='\t')
    
    # Convert numeric columns
    numeric_cols = ['id', 'proof', 'abv', 'popularity', 'avg_msrp', 'fair_price', 
                   'shelf_price', 'total_score', 'wishlist_count']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill NaN values
    df['abv'].fillna(df['proof'] / 2 if 'proof' in df.columns else 0, inplace=True)
    df['proof'].fillna(df['abv'] * 2 if 'abv' in df.columns else 0, inplace=True)
    
    # Rename columns to match our code
    df.rename(columns={
        'avg_msrp': 'msrp',
        'total_score': 'total_score'
    }, inplace=True)
    
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
