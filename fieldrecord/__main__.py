
import datetime
import logging
import os
from pathlib import Path
import shutil

import geopandas as gpd
import pandas as pd
from pathlib import Path

from fieldrecord.src.decode import decode
from fieldrecord.src.formatting import format_codes, put_codes_in_columns, merge_duplicates, sort_output_columns
from fieldrecord.src.process_points import intersect_point_data_with_plantations, join_point_data_to_polygons
from fieldrecord.src.process_polygons import intersect_polygon_data_with_plantations, clean_polygons
from fieldrecord.src.utils import read_files, set_crs, save_updated_crs_files, remove_nulls, add_nulls, timestamp, generate_summary
from fieldrecord.mappings import ABIOTIC_MAP, PEST_MAP, SEVERITY_MAP, SEVERITY_RANK, pests, columns_to_process

import typer
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger(__name__)

app = typer.Typer(name="FieldRecord")

@app.command("run")
def run_field_record(
                    plantation_path:Path,
                    manual_path:Path,
                    out_dir:Path,
                    output_crs:int=4326,
                    abiotic_map:dict[str, str] = ABIOTIC_MAP,
                    pest_map:dict[str, str] = PEST_MAP,
                    severity_map:dict[str, str] = SEVERITY_MAP,
                    severity_rank:list[str] = SEVERITY_RANK,
                    columns_to_process:dict[str, any] = columns_to_process,
                    summary=True,
                    region_col="Region",
                    district_col="DistrictName",
                    area_m_col="SHAPE_Area",
                    ):
    
    """
    Main function for running the FieldRecord program.

    This function takes in a manual data file and a plantation file, and processes the data to generate a new file
    with the same structure as the input files, but with the additional columns of 'CODE', 'CODE_dict', and the
    pests and abiotic factors processed into the desired columns.

    Parameters
    ----------
    plantation_path : Path
        Path to the plantation file.
    manual_path : Path
        Path to the manual observations data file.
    out_dir : Path
        Path to the output directory for the processed files.
    output_crs : int, optional
        The desired CRS for the output files. Defaults to 4326.
    abiotic_map : dict, optional
        The mapping of abiotic factors to their corresponding codes. Defaults to ABIOTIC_MAP, from mappings.py.
    pest_map : dict, optional
        The mapping of pest factors to their corresponding codes. Defaults to PEST_MAP, from mappings.py.
    severity_map : dict, optional
        The mapping of severity codes to their corresponding labels. Defaults to SEVERITY_MAP, from mappings.py.
    severity_rank : list, optional
        The ranking of the severity codes. Defaults to SEVERITY_RANK, from mappings.py.
    columns_to_process : dict, optional
        The columns to process in the manual data file. Defaults to columns_to_process, from mappings.py.
    summary : bool, optional
        Whether to generate a summary textfile for the data. Defaults to True.
    region_col : str, optional
        The column name for the region in the plantations file for the summary. Defaults to 'Region, which is true for HVP'.
    district_col : str, optional
        The column name for the district in the plantations file for the summary. Defaults to 'DistrictName, which is true for HVP'.
    area_m_col : str, optional
        The column name for the area in square meters in the plantations file for the summary. Defaults to 'SHAPE_Area, which is true for HVP'.

    Returns
    -------
    None
    """
    save_suffix = timestamp()
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    plantation_filename = os.path.basename(plantation_path)

    logging.info('plantation path: ' + str(plantation_filename))

    output_filename = f'{os.path.splitext(plantation_filename)[0]}_{save_suffix}.gpkg'
    
    logging.info("# --- setup: reading data...")

    # Read files
    plantations, polygons_points = read_files(plantation_path, manual_path)
    input_cols = plantations.columns.tolist()

    # Separate the observations into polygons and points, as originally it was 
    # two different layers, so the code was built for that structure 
    polygon_obs = polygons_points[polygons_points.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]
    point_obs = polygons_points[polygons_points.geometry.geom_type.isin(['Point', 'MultiPoint'])]

    # Normalise CRS for all layers involved in processing 
    plantations, point_obs, polygon_obs = set_crs(plantations, point_obs, polygon_obs, output_crs)

    # Save observation data with new CRS, and divided into separate files
    save_updated_crs_files(plantations, point_obs, polygon_obs, out_dir)

    logging.info("# --- intersect hand drawn polygons")

    polygon_obs, plantations = intersect_polygon_data_with_plantations(plantations, polygon_obs, list(columns_to_process.keys()))
    polygon_obs = clean_polygons(polygon_obs)
    polygon_obs = decode(polygon_obs, severity_map, abiotic_map, code_column='CODE') 

    logging.info("# --- intersect points")

    point_obs = intersect_point_data_with_plantations(point_obs, plantations)
    point_obs = decode(point_obs, severity_map, abiotic_map, code_column='CODE', empty_value='Trace')

    # TODO: add a check for if euc or pine pests are not in the right place

    logging.info("# --- Join point data to polygons ")

    df = join_point_data_to_polygons(point_obs=point_obs, polygon_obs=polygon_obs, attribute='CODE') 

    logging.info("# --- Format CODEs")

    # remove plantation polygons with no observations, add back in later
    df, nulls = remove_nulls(df)

    # merged all CODEs for each ID into CODE and CODE_dict
    df = merge_duplicates(df, severity_rank) 

    # put CODEs into desired format - not if this actually does anything but takes no time at all 
    df = format_codes(df, SEVERITY_MAP=severity_map, ABIOTIC_MAP=abiotic_map, PEST_MAP=pest_map, SEVERITY_RANK=severity_rank)

    # use the CODE_dict to put codes in the right columns
    df = put_codes_in_columns(df, columns_to_process, ABIOTIC_MAP=abiotic_map, PEST_MAP=pest_map, SEVERITY_RANK=severity_rank)

    # add back in nulls
    df = add_nulls(df, nulls) 

    if summary:
        # the cols should be from the Plantation df, specifying region, district, and area in m for each plantation polygon
        generate_summary(df, out_dir, region_col=region_col, district_col=district_col, area_m_col=area_m_col)
    
    # Sort output dataframe columns to include only important columns 
    df = sort_output_columns(df, input_cols, columns_to_process)

    logging.info("# --- Save outputs")

    # Save the processed dataframe to a file
    gpkg_path = out_dir / output_filename
    df.to_file(gpkg_path)

    # Save as shp too as gpkg sometimes problematic for Dave
    shp_path = (out_dir / output_filename).with_suffix(".shp")
    df.to_file(shp_path)
    
    # Save as excel
    excel_path = (out_dir / output_filename).with_suffix(".xlsx")
    df.to_excel(excel_path)

if __name__ == "__main__":
    app()
