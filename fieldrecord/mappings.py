
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
    'Med': 'Moderate',
    'High': 'High',
    'Severe': 'Severe',

}
SEVERITY_RANK = {   
    'Trace': 0,
    'Trace-Low': 1,
    'Low': 2,
    'Low-Moderate': 3,
    'Moderate': 4,
    'Moderate-High': 5,
    'High': 6,
    'High-Severe': 7,
    'Severe': 8, 
    }
# 2024
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
pests = [
    'CNC', 'DNB', 'DIP', 'IPS', 'MPA', 'PC', 'SN', 'MLS', 
    'ALS', 'DB', 'LRP', 'AGM', 'URBA', 'CupM', 'SHM', 'LeafB',
]

# Dictionary mapping short names to themselves for pest detection types
# This is done to create a consistent format for all dictionaries
PEST_MAP = {x: x for x in pests}

# List of column names to be processed
# columns_to_process = {'Sirex2023': 'SN', 'Dothi2023': 'DB', 'Abiotic2023': ABIOTIC_MAP, 'PestD_2023': PEST_MAP}
columns_to_process = {'Sirex2024': 'SN', 'Dothi2024': 'DB', 'Abiotic2024': ABIOTIC_MAP, 'PestD_2024': PEST_MAP}

