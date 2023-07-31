from datetime import datetime
import geopandas as gpd
import pandas as pd


def read_files(plantation_path, polygon_path, point_path):
    plantations = gpd.read_file(plantation_path)
    plantations = plantations.loc[plantations.geometry != None]
    point_obs = gpd.read_file(point_path)
    polygon_obs = gpd.read_file(polygon_path)
    return plantations, point_obs, polygon_obs

def set_crs(plantations, point_obs, polygon_obs,output_crs, crs=4326):
    if output_crs == 0:
        output_crs = plantations.crs
    else :
        plantations=plantations.to_crs(output_crs)
    
    # plantations = plantations.to_crs(crs)
    if point_obs.crs is None:
        point_obs.crs = crs
    if polygon_obs.crs is None:
        polygon_obs.crs = crs
    point_obs = point_obs.to_crs(output_crs)
    polygon_obs = polygon_obs.to_crs(output_crs)
    return plantations, point_obs, polygon_obs

def save_updated_crs_files(plantations, point_obs, polygon_obs, out_dir):
    # save test data with new crs
    point_obs.to_file(out_dir / 'point_obs.gpkg')
    polygon_obs.to_file(out_dir / 'polygon_obs.gpkg')
    plantations.to_file(out_dir / 'plantations.gpkg')


def remove_nulls(df):
    nulls = df[df['CODE'].isna()]
    df = df[~df['CODE'].isna()]
    return df, nulls

def add_nulls(df, nulls):
    df = pd.concat([df, nulls])
    # when duplicates from concatenation occur, keep 'df' not 'nulls'
    df = df.loc[~df.geometry.duplicated(keep='first')]
    return df

# Function to get the current timestamp
def timestamp():
    return datetime.today().strftime('%y%m%d-%H%M')
