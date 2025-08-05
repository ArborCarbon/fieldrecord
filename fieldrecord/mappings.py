import datetime 

# Dictionary mapping short names to full names for abiotic factors
ABIOTIC_MAP = {
    'Lning': 'Lightning',
    'Weed': 'Weed',
    'Storm': 'Storm',
    'FolDis': 'FoliageDiscolouration',
    'ANB': 'ANB',
    'Herb': 'Herb',
    'Miss': 'Stocking',
    'miss': 'Stocking',
    'Fire': 'Fire',
    'WL': 'WL',
    'DRT': 'DRT',
    'MY': 'MY',
}

# Dictionary mapping short names to full names for pest impact levels
SEVERITY_MAP = {
    'Trace': 'Trace',
    'Low': 'Low',
    'Moderate': 'Moderate',
    'High': 'High',
    'Severe': 'Severe',
}

# Updated for the 2024-2025 season, to include more severities
SEVERITY_RANK = {   
    'Trace': 0,
    'Trace-Low': 1,
    'Low': 2,
    'Low-Moderate': 3,
    'Low-High': 4,
    'Moderate': 5,
    'Moderate-High': 6,
    'High': 7,
    'High-Severe': 8,
    'Severe': 9, 
    }

# List of short names for pest detection types
# This list should contain all pests that are noted in the Sketch Mapping, 
# as anything not included here will be filtered out
pests = [
    'CNC', 'DNB', 'DIP', 'IPS', 'MPA', 'PC', 'SN', 'MLS', 
    'ALS', 'DB', 'LRP', 'AGM', 'URBA', 'CupM', 'SHM', 'LeafB',
    'EPB', 'EAGM', 'EMLS', 'ESHM' # euc pests, added 17/07/25
]

# Dictionary mapping short names to themselves for pest detection types
# This is done to create a consistent format for all dictionaries
PEST_MAP = {x: x for x in pests}

year = datetime.datetime.now().year

# List of column names to be processed, all pests included in this list 
# will still be included in the overall pest column, but the specific 
# severity for that pest will be included in these columns too, makes it 
# easier to do analysis later 
columns_to_process = {
    f'Sirex{year}': 'SN', 
    f'Dothi{year}': 'DB', 
    f'Aphid{year}': 'MPA',
    f'Dip{year}': 'DIP',
    f'CNC{year}': 'CNC',
    f'IPS{year}': 'IPS', 
    f'Abiotic{year}': ABIOTIC_MAP, 
    f'PestD_{year}': PEST_MAP,
}

