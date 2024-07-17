
import datetime
import logging
import os
from pathlib import Path
import shutil

import geopandas as gpd
import pandas as pd
from pathlib import Path

from fieldrecord.src.decode import decode
from fieldrecord.src.formatting import format_codes, put_codes_in_columns, sort_output_columns
from fieldrecord.src.process_points import intersect_point_data_with_plantations, join_point_data_to_polygons
from fieldrecord.src.process_polygons import intersect_polygon_data_with_plantations, clean_polygons
from fieldrecord.src.utils import read_files, set_crs, save_updated_crs_files, remove_nulls, add_nulls, timestamp
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
                    polygon_path:Path,
                    point_path:Path,
                    out_dir:Path,

                    output_crs:int=4326,
                    abiotic_map:dict[str, str] = ABIOTIC_MAP,
                    pest_map:dict[str, str] = PEST_MAP,
                    severity_map:dict[str, str] = SEVERITY_MAP,
                    severity_rank:list[str] = SEVERITY_RANK,
                    columns_to_process:dict[str, any] = columns_to_process

                    
                    ):
    
    save_suffix = timestamp()
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    plantation_filename = os.path.basename(plantation_path)
    logging.info('plantation path: ' + str(plantation_filename))
    output_filename = f'{os.path.splitext(plantation_filename)[0]}_{save_suffix}.gpkg'
    
    logging.info("# --- setup: reading data...")
    # Read files
    plantations, point_obs, polygon_obs = read_files(plantation_path, polygon_path, point_path)
    input_cols = plantations.columns.tolist()

    # Set crs'
    plantations, point_obs, polygon_obs = set_crs(plantations, point_obs, polygon_obs, output_crs)
    save_updated_crs_files(plantations, point_obs, polygon_obs, out_dir)


    logging.info("# --- intersect hand drawn polygons")
    polygon_obs, plantations = intersect_polygon_data_with_plantations(plantations, polygon_obs, list(columns_to_process.keys()))
    polygon_obs = clean_polygons(polygon_obs)
    # decode polygons
    polygon_obs = decode(polygon_obs, severity_map, code_column='CODE')


    logging.info("# --- intersect points")
    point_obs = intersect_point_data_with_plantations(point_obs, plantations)
    # decode points
    point_obs = decode(point_obs, severity_map, code_column='CODE', empty_value='Trace')


    logging.info("# --- Join point data to polygons ")
    df = join_point_data_to_polygons(point_obs=point_obs, polygon_obs=polygon_obs, attribute='CODE')


    logging.info("# --- Format CODEs")
    # remove empty CODEs for formatting, add back in later
    df, nulls = remove_nulls(df)

    # put CODEs into desired format
    df = format_codes(df, SEVERITY_MAP=severity_map, ABIOTIC_MAP=abiotic_map, PEST_MAP=pest_map, SEVERITY_RANK=severity_rank)
    df = put_codes_in_columns(df, columns_to_process, SEVERITY_RANK=severity_rank)

    # add empty CODEs back in
    df = add_nulls(df, nulls)
    

    logging.info("# --- Save outputs")
    # drop cols
    df = sort_output_columns(df, input_cols, columns_to_process)
    # Save the processed dataframe to a file
    gpkg_path = out_dir / output_filename
    df.to_file(gpkg_path)

    # NH: Save as shp too as gpkg sometimes problematic for Dave
    shp_path = (out_dir / output_filename).with_suffix(".shp")
    df.to_file(shp_path)
    
    excel_path = (out_dir / output_filename).with_suffix(".xlsx")
    df.to_excel(excel_path)

    # produce pest info csv 
    # print(df.head(6))
    # print(df.columns)
if __name__ == "__main__":
    app()