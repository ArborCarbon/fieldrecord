#!/usr/bin/env ipython 
# %%
import geopandas as gpd
import pandas as pd
from pathlib import Path

from fieldrecord.src.decode import decode
from fieldrecord.src.formatting import format_codes, put_codes_in_columns, sort_output_columns
from fieldrecord.src.process_points import intersect_point_data_with_plantations, join_point_data_to_polygons
from fieldrecord.src.process_polygons import intersect_polygon_data_with_plantations, clean_polygons
from fieldrecord.src.utils import read_files, set_crs, save_updated_crs_files, remove_nulls, add_nulls, timestamp


# --- Inputs
# File paths 
plantation_path = Path('/Users/harryeslick/ArborCarbon Dropbox/Consulting/ACTForests/2023/NSA2023/NSA2023.shp')
polygon_path = Path('/Users/harryeslick/ArborCarbon Dropbox/Consulting/ACTForests/2023/070223/164436/area_valid.fgb')
point_path = Path('/Users/harryeslick/ArborCarbon Dropbox/Consulting/ACTForests/2023/070223/164436/mpoint.shp')

# gdf = gpd.read_file(polygon_path)

# Set crs, and read data from files
crs = 4326


# --- Outputs
# Create output directory if it does not exist
save_suffix = timestamp()
out_dir = Path(f'/Users/harryeslick/ArborCarbon Dropbox/Consulting/ACTForests/2023/fieldrecord3')
out_dir.mkdir(exist_ok=True, parents=True)
output_filename = f'{plantation_path.stem}_{save_suffix}.gpkg'




# ----------------------------------------------------------
# ---------------------- Mappings -----------------------------
# ----------------------------------------------------------

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
columns_to_process = {'Sirex_Im_1': 'SN', 'DothiImp22': 'DB', 'Abiotic22': ABIOTIC_MAP, 'Pest_Det_1': PEST_MAP}




# ----------------------------------------------------------
# ---------------------- Main -----------------------------
# ----------------------------------------------------------

def main():

    # --- setup
    # Read files
    plantations, point_obs, polygon_obs = read_files(plantation_path, polygon_path, point_path)
    input_cols = plantations.columns.tolist()
    # Set crs'
    plantations, point_obs, polygon_obs = set_crs(plantations, point_obs, polygon_obs, crs)
    save_updated_crs_files(plantations, point_obs, polygon_obs, out_dir)


    # --- intersect hand drawn polygons
    polygon_obs, plantations = intersect_polygon_data_with_plantations(plantations, polygon_obs, list(columns_to_process.keys()))
    polygon_obs = clean_polygons(polygon_obs)
    # decode polygons
    polygon_obs = decode(polygon_obs, SEVERITY_MAP, code_column='CODE')


    # --- intersect points
    point_obs = intersect_point_data_with_plantations(point_obs, plantations)
    # decode points
    point_obs = decode(point_obs, SEVERITY_MAP, code_column='CODE', empty_value='Trace')


    # --- Join point data to polygons 
    df = join_point_data_to_polygons(point_obs=point_obs, polygon_obs=polygon_obs, attribute='CODE')


    # --- Format CODEs
    # remove empty CODEs for formatting, add back in later
    df, nulls = remove_nulls(df)

    # put CODEs into desired format
    df = format_codes(df, SEVERITY_MAP=SEVERITY_MAP, ABIOTIC_MAP=ABIOTIC_MAP, PEST_MAP=PEST_MAP, SEVERITY_RANK=SEVERITY_RANK)
    df = put_codes_in_columns(df, columns_to_process, SEVERITY_RANK=SEVERITY_RANK)

    # add empty CODEs back in
    df = add_nulls(df, nulls)
    print('x')

    # --- Save outputs
    # drop cols

    
    df = sort_output_columns(df, input_cols, columns_to_process)
    
    # Save the processed dataframe to a file
    df.to_file(out_dir / output_filename)
    return df


x = main()

