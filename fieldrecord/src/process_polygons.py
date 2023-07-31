import geopandas as gpd





# --------------------------------------------------------------------
# -------------- Find Meaningful Polygons Functions -----------------
# --------------------------------------------------------------------

def preprocess_geodataframes(plantations, polygon_obs, observation_attributes, columns_to_process):
    """
    Preprocesses the plantation and observation GeoDataFrames by performing necessary operations before intersection.

    Args:
        plantations (GeoDataFrame): DataFrame containing plantation polygons.
        polygon_obs (GeoDataFrame): DataFrame containing observation polygons.
        observation_attributes (list): Attributes to join to plantations.

    Returns:
        tuple: (modified plantations, modified polygon_obs, bool indicating if code exists in plantations)
    """

    plantations = plantations.copy()
    polygon_obs = polygon_obs.copy()
    plantations[columns_to_process] = 'None' # initialise all columns to process to None
    plantations['geometry'] = plantations.buffer(0)
    plantations['p_area'] = plantations.area

    observation_attributes.extend(['geometry'])
    # polygon_obs = polygon_obs[observation_attributes]
    polygon_obs['obs_idx'] = list(polygon_obs.reset_index()['index'])

    return plantations, polygon_obs


def perform_intersection(plantations, polygon_obs):
    """
    Performs intersection between plantations and polygon_obs.

    Args:
        plantations (GeoDataFrame): DataFrame containing plantation polygons.
        polygon_obs (GeoDataFrame): DataFrame containing observation polygons.
        code_code (str): The code attribute to join to plantations.

    Returns:
        GeoDataFrame: DataFrame containing the intersection between plantations and polygon_obs.
    """
    intersection_df = gpd.sjoin(plantations, polygon_obs, how='left', predicate='intersects')
    # drop and rename columns
    # intersection_df.drop(columns=['CODE_1'], inplace=True)
    # intersection_df.rename(columns={'CODE_2': 'CODE'}, inplace=True)
    return intersection_df



def find_largest_intersection(intersection_df):
    """
    Finds the largest intersecting part from each observation in polygon_obs.

    Args:
        intersection_df (GeoDataFrame): DataFrame containing the intersection between plantations and polygon_obs.

    Returns:
        GeoDataFrame: DataFrame containing the largest intersecting part from each observation.
    """
    intersection_df['intersection_area'] = intersection_df.area
    intersection_df.sort_values(by='intersection_area', inplace=True)
    largest_intersection = intersection_df.drop_duplicates(subset='obs_idx', keep='last')

    return largest_intersection

def find_features_above_threshold(intersection_df, largest_intersection, min_area, percent_overlap):
    """
    Finds rows with area greater than min_area or overlap greater than percent_overlap.

    Args:
        intersection_df (GeoDataFrame): DataFrame containing the intersection between plantations and polygon_obs.
        min_area (int): Minimum area of intersection threshold; areas above this are kept.
        percent_overlap (float): Threshold for overlap between plantations and polygon_obs; shapes above threshold are kept.

    Returns:
        GeoDataFrame: DataFrame containing features above the specified thresholds.
    """
    remaining_features = intersection_df.loc[~intersection_df.index.isin(largest_intersection.index)]
    features_above_threshold = remaining_features.loc[
        (remaining_features.intersection_area > min_area)
        | ((remaining_features.intersection_area / remaining_features.p_area) > percent_overlap)
    ]

    return features_above_threshold

def intersect_polygon_data_with_plantations(
    plantations: gpd.GeoDataFrame,
    polygon_obs: gpd.GeoDataFrame,
    columns_to_process: list[str],
    observation_attributes: list[str] = ['CODE'],
    min_area: int = 2000,
    percent_overlap: float = 0.5
) -> gpd.GeoDataFrame:
    """
    Finds meaningful intersections between forest plantation boundaries (plantations)
    and rough hand-drawn field observations (polygon_obs).
    Calls the smaller functions defined above to perform specific tasks.

    Args:
        plantations (GeoDataFrame): DataFrame to which attributes from polygon_obs are added.
        polygon_obs (GeoDataFrame): DataFrame with field observations to transfer to overlapping parts of plantations.

    Keyword Args:
        observation_attributes (list): Attributes to join to plantations (default: ['CODE']).
        min_area (int): Minimum area of intersection threshold; areas above this are kept (default: 2000).
        percent_overlap (float): Threshold for overlap between plantations and polygon_obs; shapes above threshold are kept (default: 0.5).

    Returns:
        GeoDataFrame: plantations with additional attribute columns from polygon_obs.
    """

    plantations, polygon_obs = preprocess_geodataframes(plantations, polygon_obs, observation_attributes, columns_to_process)

    intersection_df = perform_intersection(plantations, polygon_obs)
    
    #TODO: add meaningful intersections back in. Drop intersections less than threshold
    # largest_intersection = find_largest_intersection(intersection_df)

    # features_above_threshold = find_features_above_threshold(intersection_df, largest_intersection, min_area, percent_overlap)

    # result = pd.concat([features_above_threshold, largest_intersection], ignore_index=True)
    # result = result.drop(['p_area', 'intersection_area'], axis=1)

    return intersection_df, plantations




def clean_polygons(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Cleans up the polygons in a GeoDataFrame by removing invalid geometries and dropping duplicates.
    
    Args:
        gdf (GeoDataFrame): The input GeoDataFrame.
        
    Returns:
        GeoDataFrame: The cleaned-up GeoDataFrame.
    """
    gdf = gdf.copy()
    gdf = gdf[gdf['geometry'] != 'None']
    gdf = gdf[gdf['geometry'].is_valid]
    gdf.reset_index(inplace=True)
    #TODO: why are there duplicates? should these be sorted by severity to keep most severe?
    gdf.drop_duplicates(subset=['obs_idx', 'index'], keep='last', inplace=True)
    return gdf.drop(columns=['index'])
