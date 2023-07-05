import pandas as pd


# ---------- Decode CODE Column
# -------------------------------
def decode(gdf, SEVERITY_MAP: dict, code_column='CODE', empty_value='None'):
    """
    Decodes the CODE column of a GeoDataFrame based on the provided mapping dictionaries, and updates the specified columns
    with the decoded values.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame containing the CODE column.
        SEVERITY_MAP (dict): A dictionary mapping severity codes to their corresponding values.
        ABIOTIC_MAP (dict): A dictionary mapping abiotic codes to their corresponding values.
        PEST_MAP (dict): A dictionary mapping pest codes to their corresponding values.
        code_column (str, optional): Name of the CODE column, default is 'CODE'.

    Returns:
        GeoDataFrame: A copy of the input GeoDataFrame with the decoded values in the specified columns.
    """
    gdf = gdf.copy()
    gdf = gdf[gdf['geometry'] != 'None']
    gdf = gdf[~gdf['geometry'].isna()]
    nulls = gdf[gdf['CODE'].isna()]
    gdf = gdf[~gdf['CODE'].isna()]
    gdf['CODE'] = gdf['CODE'].str.strip()


    def get_maps(x, severity_map, code_column, empty_value='None'):
        code = x[code_column]
        split = code.split('_')[:-1]
        decode = build_decode_list(code, split, severity_map)
        result = process_decode(decode, split, empty_value)
        return result        

    def build_decode_list(code, split, severity_map):
        decode = ['other' if x not in severity_map else 'severity' for x in split]
        return decode


    def process_decode(decode, split, empty_value='None'):
        result = {}
        keys = []
        severity_values = []

        for d, s in zip(decode, split):
            if d == 'other':
                if severity_values:
                    for key in keys:
                        result[key] = severity_values
                    keys = []
                    severity_values = []
                keys.append(s)
            elif d == 'severity':
                severity_values.append(s)

        # Assign the remaining severity values to the keys
        if severity_values:
            if not keys:
                result['no-severity'] = severity_values
            for key in keys:
                result[key] = severity_values
        else:
            for key in keys:
                result[key] = [empty_value]
        return result



    def apply_maps(gdf, _map, code_column, empty_value='None'):
        gdf['CODE_dict'] = gdf.apply(lambda x: get_maps(x, _map, code_column, empty_value), axis=1)
        return gdf

    gdf = apply_maps(gdf, SEVERITY_MAP, code_column=code_column, empty_value=empty_value)
  
    gdf = pd.concat([gdf, nulls])
    return gdf

