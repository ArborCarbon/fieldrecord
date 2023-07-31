import geopandas as gpd
import pandas as pd
from shapely.prepared import prep


def intersect_point_data_with_plantations(point_obs, plantations):    
    # ony keep important columns in point data
    point_obs = point_obs[['CODE', 'geometry']]

    # fillna in CODE column
    # point_obs['CODE'] = point_obs['CODE'].fillna('NOCODE_')
    point_obs.dropna(inplace=True)
    # point_obs = point_obs[~point_obs['CODE'].isna()]

    def decode_points(x, code_column='CODE'):
        x[code_column] = x[code_column].strip()
        split = x[code_column].split('_')[:-1]
        x['CODE_dict'] = {code: ["Trace"] for code in split}
        return x

    point_obs = point_obs.apply(lambda x: decode_points(x), axis=1)
    
    # intersect point data with plantations
    point_obs = gpd.sjoin(plantations, point_obs, how='inner', predicate='intersects')
    point_obs.drop(columns=['index_right',], inplace=True)
    # point_obs.rename(columns={'CODE_right': 'CODE'}, inplace=True)

    return point_obs



def join_point_data_to_polygons(
    point_obs: gpd.GeoDataFrame,
    polygon_obs: gpd.GeoDataFrame,
    attribute: str
) -> gpd.GeoDataFrame:
    """
    Joins point data to polygons without duplicating any points.

    Args:
        point_obs (GeoDataFrame): DataFrame with point data.
        polygon_obs (GeoDataFrame): DataFrame with polygon data.
        attribute (str): The attribute name to join.

    Returns:
        GeoDataFrame: DataFrame with joined point and polygon data.
    """
    point_obs[attribute] = point_obs[attribute].fillna(value='NOCODE_')

    polygons_with_CODE = polygon_obs.loc[~polygon_obs['CODE'].isna()]
    polygons_without_CODE = polygon_obs.loc[polygon_obs['CODE'].isna()]

    prepared_polygon = prep(polygons_with_CODE.geometry.buffer(0).unary_union)
    hit_index = point_obs["geometry"].apply(lambda x: prepared_polygon.intersects(x))
    point_obs = point_obs[~hit_index]

    # Reset the index of the polygon_obs 
    polygon_obs = polygon_obs.reset_index()

    # concatenate polygon_obs and point_obs
    joined_gdf = gpd.GeoDataFrame(pd.concat([polygons_with_CODE, polygons_without_CODE, point_obs], ignore_index=True), crs=polygon_obs.crs)    
   
    # drop and rename join columns
    # joined_gdf.drop(columns=['index'], inplace=True)
    joined_gdf.rename(columns={'CODE_left': 'CODE'}, inplace=True)

    return joined_gdf

