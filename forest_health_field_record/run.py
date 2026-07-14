from forest_health_field_record.main import run_field_record
from pathlib import Path 
from forest_health_field_record.mappings import ABIOTIC_MAP, PEST_MAP, SEVERITY_MAP, SEVERITY_RANK, pests, columns_to_process
import geopandas as gpd 
import fiona
import pandas as pd

pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
output_dir = pp / 'output_220525'
manual_path = pp / '220525/GT-2025-05-22T02_06_29.834Z.geojson'
plantations_path = pp / '220525/Dataset_David.gdb'

# gdf.rename(columns={'classification':'CODE'}, inplace=True)

run_field_record(plantation_path=str(plantations_path), 
                manual_path=str(manual_path), 
                out_dir=str(output_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process)


# rclone copy -P "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/output_220525" "dropbox:/Consulting/SAUniForestry/2025/joined_IR"



# rclone copy -P "dropbox:/Consulting/SAUniForestry/2025/Flightdata/Day4" "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/220525"
# rclone copy -P "dropbox:/Consulting/SAUniForestry/2025/Dataset_David.gdb (2)" "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/220525"


# rclone copy -P "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/NavData" "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/220525_gipps"
# rclone copy -P "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/output_230525_gipps" "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/joined_IR_230525"

pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
output_dir = pp / 'output_230525_gipps'
manual_path = pp / '220525_gipps/input2.gpkg'
plantations_path = '/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/data1/GippsPlantationLayer.gpkg'

# gdf.rename(columns={'classification':'CODE'}, inplace=True)

run_field_record(plantation_path=str(plantations_path), 
                manual_path=str(manual_path), 
                out_dir=str(output_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process)

# testing to fix bug 
pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
out_dir = pp / '170725'
out_dir.mkdir(exist_ok=True, parents=True)

plantations_path='/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/HVPPlantationLayer/Plantation_20250617.gdb/Plantation_20250617.gdb'
plantations = gpd.read_file(plantations_path, layer=1)
plantations_0 = gpd.read_file(plantations_path, layer=0)
plantations_combined = pd.concat([plantations_0, plantations]).reset_index(drop=True)
plantations_0.to_file(out_dir / 'GippsPlantationLayer_layer0.gpkg')

gdf1 = gpd.read_file('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/Gippsland-2025-07-17T00_41_55.118Z.geojson')
gdf2 = gpd.read_file('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/GT-2025-07-17T00_44_51.158Z.geojson')

gdf3_1 = gpd.read_file('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/North East-2025-07-17T00_42_43.673Z.geojson', rows=slice(0,559))
gdf3_2 = gpd.read_file('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/North East-2025-07-17T00_42_43.673Z.geojson', rows=slice(561,None))
gdf3 = pd.concat([gdf3_1, gdf3_2])
gdf3.reset_index(drop=True, inplace=True)

gdf4 = gpd.read_file('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/WesternV2-2025-07-17T00_43_16.176Z.geojson')

manual = pd.concat([gdf1, gdf2, gdf3, gdf4]).reset_index(drop=True)
manual.to_file(out_dir / 'manual.gpkg')

# import json
# with open('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/Aerialdata/North East-2025-07-17T00_42_43.673Z.geojson') as fh:
#     data = json.loads(fh.read())

# polygons = [feature for feature in data["features"] if feature["geometry"]["type"] == "Polygon"]
# for polygon in polygons:
#     if polygon["geometry"]["coordinates"][0] != polygon["geometry"]["coordinates"][-1]:
#         print("a")
# data["features"][559]



manual_path= str(out_dir / 'manual.gpkg')
plantation_path = str(out_dir / 'GippsPlantationLayer_layer0.gpkg')

# gdf.rename(columns={'classification':'CODE'}, inplace=True)

run_field_record(plantation_path=str(plantations_path), 
                manual_path=str(manual_path), 
                out_dir=str(out_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process)


# rclone copy -P dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/Aerialdata /home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff




# -------------------------------- 25/07/2025 -------------------------------- #


# rclone copy -P dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/Aerialdata/2025072025 /home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725
# rclone copy -P "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/AKDPlantationLayer/2025 AKD Arbocarbon Health Survey" /home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/akd
# rclone copy -P "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/HVPPlantationLayer" /home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/hvp

# Plantation_20250617

akd=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/akd/2025 AKD Arbocarbon Health Survey.shp")
# make an index called global id
akd['GlobalID'] = akd.index
akd.to_file(out_dir/"AKDPlantationLayer.gpkg")

hvp=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/hvp/Plantation_20250617.gdb/Plantation_20250617.gdb", layer=1)
hvp.to_file(out_dir/"HVPPlantationLayer.gpkg")

gdf=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/Gippsland (Imported)-2025-07-23T03_34_30.024Z.geojson")
gdf1=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/GT (Imported)-2025-07-23T04_36_23.781Z.geojson")
gdf2=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/North East (Imported)-2025-07-23T03_57_07.929Z.geojson", rows=slice(0,559))
gdf3=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/North East (Imported)-2025-07-23T03_57_07.929Z.geojson", rows=slice(560,None))
gdf4=gpd.read_file("/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/WesternV2 (Imported)-2025-07-23T04_10_16.819Z.geojson")
gdf5 = pd.concat([gdf, gdf1, gdf2, gdf3, gdf4]).reset_index(drop=True)

# remove datetime col
gdf5.rename(columns={'classification':'CODE'}, inplace=True)
gdf6 = gdf5[['CODE', 'id','geometry']]

gdf6.to_file(pp/"240725/manual.gpkg")

pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
out_dir = pp / '240725/hvp_out'
out_dir.mkdir(exist_ok=True, parents=True)
manual_path= str(pp / '240725/manual.gpkg')
plantation_path = str(out_dir / 'HVPPlantationLayer.gpkg')

out_dir = pp / '240725/akd_out'
out_dir.mkdir(exist_ok=True, parents=True)
manual_path= str(pp / '240725/manual.gpkg')
plantation_path = str(out_dir / 'AKDPlantationLayer.gpkg')

run_field_record(plantation_path=str(plantation_path), 
                manual_path=str(manual_path), 
                out_dir=str(out_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process,
                gen_summary=False)

# rclone copy -P "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/hvp_out" "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/Aerialdata/HVP_output_IR"
# rclone copy -P "/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/240725/akd_out" "dropbox:/Consulting/HVPPlantations/HVP_J22690_FHSProgram/2025/End_Survey_Data/Aerialdata/AKD_output_IR"


# ------------------------------- testing 28/07 ------------------------------ #

pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
out_dir = pp / '280725'
out_dir.mkdir(exist_ok=True, parents=True)
manual_path= str(pp / '240725/manual.gpkg')
plantation_path = str(pp / '240725/hvp_out/HVPPlantationLayer.gpkg')

run_field_record(plantation_path=str(plantation_path), 
                manual_path=str(manual_path), 
                out_dir=str(out_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process,
                summary=True)




# ------------------------------ run 26/09/2025 ------------------------------ #
pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff')
manual_path = str(pp / 'North East Dothi-2025-09-25T13_03_31.129Z.geojson')
plantation_path = str(pp / '240725/hvp_out/HVPPlantationLayer.gpkg')
out_dir = pp / '260925'
out_dir.mkdir(exist_ok=True, parents=True)

man=gpd.read_file(manual_path)
# replace all rows with code Low_Trace_DNB with Trace_DNB
man.loc[man['CODE'] == 'Low_Trace_DNB', 'CODE'] = 'Trace_DNB'

run_field_record(plantation_path=str(plantation_path), 
                manual_path=str(manual_path), 
                out_dir=str(out_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process,
                summary=True)



# ------------------------------ run 26/09/2025 ------------------------------ #
pp = Path('/home/arborcarbon/BigFella/Development/IR/fieldrecord_stuff/20-11-2025/')

gdf1 = gpd.read_file(pp / 'ACT-2025-11-20T03_07_34.072Z.geojson')
gdf2 = gpd.read_file(pp / 'gps-serial-trail-ACT-2025-11-20T03-07-38-134Z.geojson')
gdf = pd.concat([gdf1, gdf2]).reset_index(drop=True)
gdf.rename(columns={'classification':'CODE'}, inplace=True)
gdf.to_file(pp / 'combined.geojson')

p = gpd.read_file(pp / 'ACTForestHealthLayer25/ACTForestHealthLayer25.gdb', layer=0)
p.to_file(pp / "ACT_Plantation.gpkg")

manual_path = str(pp / 'combined.geojson')
plantation_path = str(pp / 'ACT_Plantation.gpkg')
out_dir = pp / 'ACT_output_20-11-2025/'
out_dir.mkdir(exist_ok=True, parents=True)

man=gpd.read_file(manual_path)
# replace all rows with code Low_Trace_DNB with Trace_DNB
# man.loc[man['CODE'] == 'Low_Trace_DNB', 'CODE'] = 'Trace_DNB'

run_field_record(plantation_path=str(plantation_path), 
                manual_path=str(manual_path), 
                out_dir=str(out_dir), 
                abiotic_map=ABIOTIC_MAP, 
                pest_map=PEST_MAP, 
                severity_map=SEVERITY_MAP, 
                severity_rank=SEVERITY_RANK, 
                columns_to_process=columns_to_process,
                region_col=None,
                district_col=None,
                area_hec_col="Shape_Area",
                summary=True)


