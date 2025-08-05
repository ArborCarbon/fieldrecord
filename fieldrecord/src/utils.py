from datetime import datetime
import geopandas as gpd
import pandas as pd


def read_files(plantation_path, manual_path):
    if plantation_path.endswith == '.gdb':
        plantations = gpd.read_file(plantation_path, layer=0)
    else:
        plantations = gpd.read_file(plantation_path)
        print("Opened")
    plantations = plantations.loc[plantations.geometry != None]
    polygons_points = gpd.read_file(manual_path)
    return plantations, polygons_points

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

    # make all nulls or nones the same for all columns - might not work
    for col in df.columns:
        df[col] = None if df[col].isna().all() else df[col]
    return df

def generate_summary(df, out_dir, region_col="Region", district_col="DistrictName", area_m_col="SHAPE_Area"):
    # for each region - total sirex, mpa, cnc, dip, ips, anb, dnb (but check)
    # for each region euc only - but shouldn't have to check - 'EPB', 'EMLS'
    # for each region total area affected & total area not affected
    with open(out_dir / "summary.txt", "w") as f:
        f.write("-------- REGION SUMMARY --------\n")
        df['area_hec'] = df[area_m_col] / 10000
        for region in df[region_col].unique():
            s = df[df[region_col] == region]
            s_null = s[s['CODE'].isna()]
            s_valid = s[s['CODE'].notna()]
            f.write(f"{region}:\n")
            f.write(f"\tTotal area in region: {s['area_hec'].sum()} hectares\n")
            f.write(f"\tTotal area affected: {s_valid['area_hec'].sum()} hectares\n")
            f.write(f"\tTotal area not affected: {s_null['area_hec'].sum()} hectares\n")
            f.write(f"\tPest Summary for {region}:\n")
            for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
                s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
                f.write(f"\t\t{pest} {s_pest['area_hec'].sum()} hectares\n")
            f.write("\n")

        f.write("-------- DISTRICT SUMMARY --------\n")
        for district in df[district_col].unique():
            s = df[df[district_col] == district]
            s_null = s[s['CODE'].isna()]
            s_valid = s[s['CODE'].notna()]
            f.write(f"{district}:\n")
            f.write(f"\tTotal area in district: {s['area_hec'].sum()} hectares\n")
            f.write(f"\tTotal area affected: {s_valid['area_hec'].sum()} hectares\n")
            f.write(f"\tTotal area not affected: {s_null['area_hec'].sum()} hectares\n")
            f.write(f"\tPest Summary for {district}:\n")
            for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
                s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
                f.write(f"\t\t{pest} {s_pest['area_hec'].sum()} hectares\n")
            f.write("\n")

# Function to get the current timestamp
def timestamp():
    return datetime.today().strftime('%y%m%d-%H%M')
 