
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

# List of short names for pest detection types
pests = [
    'CNC', 'DNB', 'DIP', 'IPS', 'MPA', 'PC', 'SN', 'MLS', 
    'ALS', 'DB', 'LRP', 'AGM', 'URBA', 'CupM', 'SHM', 'LeafB',
]

# Dictionary mapping short names to themselves for pest detection types
# This is done to create a consistent format for all dictionaries
PEST_MAP = {x: x for x in pests}

# List of column names to be processed
columns_to_process = {'Sirex_Impact_2023': 'SN', 'Dothi_Impact_2023': 'DB', 'Abiotic_2023': ABIOTIC_MAP, 'Pest_Detected_2023': PEST_MAP}

