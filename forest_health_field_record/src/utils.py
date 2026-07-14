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

def prepare_plantations(plantations):
    if 'GlobalID' not in plantations.columns:
        plantations['GlobalID'] = plantations.index
    return plantations

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

def generate_summary(df, out_dir, region_col=None, district_col=None, area_hec_col="SHAPE_Area"):
    # for each region - total sirex, mpa, cnc, dip, ips, anb, dnb (but check)
    # for each region euc only - but shouldn't have to check - 'EPB', 'EMLS'
    # for each region total area affected & total area not affected

    summary_df = pd.DataFrame(columns=["Cause", "Year", "Hectares", "Region", "District"])
    s_null = df[df['CODE'].isna()]
    s_valid = df[df['CODE'].notna()]
    summary_df.loc[len(summary_df)] = ["Total Affected", datetime.today().year, s_valid[area_hec_col].sum(), None, None]
    summary_df.loc[len(summary_df)] = ["Total Not Affected", datetime.today().year, s_null[area_hec_col].sum(), None, None]

    for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
        s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
        summary_df.loc[len(summary_df)] = [pest, datetime.today().year, s_pest[area_hec_col].sum(), None, None]

    if region_col:
        for region in df[region_col].unique():
            s_null = df[df[region_col] == region][df['CODE'].isna()]
            s_valid = df[df[region_col] == region][df['CODE'].notna()]
            summary_df.loc[len(summary_df)] = ["Total Affected", datetime.today().year, s_valid[area_hec_col].sum(), region, None]
            summary_df.loc[len(summary_df)] = ["Total Not Affected", datetime.today().year, s_null[area_hec_col].sum(), region, None]

            for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
                s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
                summary_df.loc[len(summary_df)] = [pest, datetime.today().year, s_pest[area_hec_col].sum(), region, None]

    if district_col:
        for district in df[district_col].unique():
            s_null = df[df[district_col] == district][df['CODE'].isna()]
            s_valid = df[df[district_col] == district][df['CODE'].notna()]
            summary_df.loc[len(summary_df)] = ["Total Affected", datetime.today().year, s_valid[area_hec_col].sum(), None, district]
            summary_df.loc[len(summary_df)] = ["Total Not Affected", datetime.today().year, s_null[area_hec_col].sum(), None, district]

            for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
                s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
                summary_df.loc[len(summary_df)] = [pest, datetime.today().year, s_pest[area_hec_col].sum(), None, district]

    summary_df.to_csv(out_dir / "summary.csv", index=False)
    # NOTE: old summary code - txt file not csv 
    # with open(out_dir / "summary.txt", "w") as f:
    #     if region_col:
    #         f.write("-------- REGION SUMMARY --------\n")
    #         for region in df[region_col].unique():
    #             s = df[df[region_col] == region]
    #             s_null = s[s['CODE'].isna()]
    #             s_valid = s[s['CODE'].notna()]
    #             f.write(f"{region}:\n")
    #             f.write(f"\tTotal area in region: {s[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tTotal area affected: {s_valid[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tTotal area not affected: {s_null[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tPest Summary for {region}:\n")
    #             for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
    #                 s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
    #                 f.write(f"\t\t{pest} {s_pest[area_hec_col].sum()} hectares\n")
    #             f.write("\n")

    #     if district_col:
    #         f.write("-------- DISTRICT SUMMARY --------\n")
    #         for district in df[district_col].unique():
    #             s = df[df[district_col] == district]
    #             s_null = s[s['CODE'].isna()]
    #             s_valid = s[s['CODE'].notna()]
    #             f.write(f"{district}:\n")
    #             f.write(f"\tTotal area in district: {s[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tTotal area affected: {s_valid[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tTotal area not affected: {s_null[area_hec_col].sum()} hectares\n")
    #             f.write(f"\tPest Summary for {district}:\n")
    #             for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
    #                 s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
    #                 f.write(f"\t\t{pest} {s_pest[area_hec_col].sum()} hectares\n")
    #             f.write("\n")

    #     if not region_col and not district_col:
    #         f.write("-------- OVERALL SUMMARY --------\n")
    #         s_null = df[df['CODE'].isna()]
    #         s_valid = df[df['CODE'].notna()]
    #         f.write(f"\tTotal area: {df[area_hec_col].sum()} hectares\n")
    #         f.write(f"\tTotal area affected: {s_valid[area_hec_col].sum()} hectares\n")
    #         f.write(f"\tTotal area not affected: {s_null[area_hec_col].sum()} hectares\n")
    #         f.write(f"\tPest Summary:\n")
    #         for pest in ['SN', 'MPA', 'CNC', 'DIP', 'IPS', 'ANB', 'DNB']:
    #             s_pest = s_valid[s_valid['CODE'].str.contains(pest, na=False)]
    #             f.write(f"\t\t{pest} {s_pest[area_hec_col].sum()} hectares\n")
    #         f.write("\n")

# Function to get the current timestamp
def timestamp():
    return datetime.today().strftime('%y%m%d-%H%M')

def at_risk_sirex(df):
    # hvp Species split on space 0 index 601 is the only one 
    # akd Species PRAD and Status Planted 
    # act YOP, THIN_STS "Unthinned"
    df = df.to_crs(7855)
    sirex_col = f"Sirex{datetime.now().year}"
    has_sirex = (df[sirex_col].notna()) & (df[sirex_col] != "None")

    if 'PlantYear' in df.columns and 'OperationClass' in df.columns: # HVP
        plant_col = 'PlantYear'
        age_col = 'Age'
        thin_col = 'OperationClass'
        species_col = 'Species'
        df[age_col] = df[plant_col].apply(lambda x: datetime.now().year - int(x) if (x and int(x) != 0) else None)
        eligible = (
            (df[sirex_col].isna() | (df[sirex_col] == "None"))
            & (df[age_col].between(9, 18, inclusive="both")) 
            & (~df[thin_col].isin(["T1", "T2", "T3", "T4"]))
            & (df[species_col].split(" ")[0].astype(int) == 601) # not tested 
        )

    elif 'Plant_Year' in df.columns and 'Thinning_S' in df.columns: # AKD
        plant_col = 'Plant_Year'
        age_col = 'Age'
        thin_col = 'Thinning_S'
        species_col = 'Species'
        status_col = 'Status'
        df[age_col] = df[plant_col].apply(lambda x: datetime.now().year - int(x) if (x and int(x) != 0) else None)
        eligible = (
            (df[sirex_col].isna() | (df[sirex_col] == "None"))
            & (df[age_col].between(9, 18, inclusive="both")) 
            & (~df[thin_col].isin(["T1", "T2", "T3", "T4"]))
            & (df[status_col] == "Planted")
            & (df[species_col] == "PRAD") 
        )

    elif 'YOP' in df.columns and 'THIN_STS' in df.columns: # ACT
        plant_col = "YOP"
        age_col = "AGE"
        thin_col = "THIN_STS"
        df[age_col] = df[plant_col].apply(lambda x: datetime.now().year - int(x) if (x and int(x) != 0) else None)
        eligible = (
            (df[sirex_col].isna() | (df[sirex_col] == "None"))
            & (df[age_col].between(9, 18, inclusive="both")) 
            & (df[thin_col] == "Unthinned") # no species 
        )

    elif 'Establishm' and 'Thinning_S' in df.columns: # GT
        plant_col = 'Establishm'
        thin_col = 'Thinning_S'
        species_col = 'Primaryspe'
        df[age_col] = df[plant_col].apply(lambda x: datetime.now().year - int(x) if (x and int(x) != 0) else None)
        eligible = (
            (df[sirex_col].isna() | (df[sirex_col] == "None"))
            & (df[age_col].between(9, 18, inclusive="both")) 
            & (df[thin_col].isin(["UT", "Unthi",]))
            & (df[species_col] == "Pine")
        )

    else:
        raise ValueError("No PlantYear or Plant_Year column found in dataframe (need to define in at_risk_sirex() in utils.py)")

    # 2 km buffer around all compartments with any Sirex value
    sirex_buffer = (
        df.loc[has_sirex, "geometry"]
        .buffer(2000)
        .union_all()
    )

    # find eligible compartments within 2 km and update values
    at_risk = eligible & df.geometry.intersects(sirex_buffer)
    df.loc[at_risk, sirex_col] = "At Risk"
    df=df.to_crs(4326)
    return df
