

# pp = Path('/home/arborcarbon/BigFella/Development/IR')
# region_col = 'Region'
# district_col = 'DistrictName'
# code_col = 'CODE'
# area_col = 'SHAPE_Area'



# -------------------------- CREATE SEVERITY COLUMN -------------------------- #

def run_graphs_and_plots(out_dir, region_col, district_col, code_col, area_col, year, pest_area_path, final_pest_area_path):
    from pathlib import Path 
    import geopandas as gpd 
    import pandas as pd
    import re 
    import os

    df = pd.read_excel(pest_area_path)
    
    severity_map = {
        "Trace_Low": 1,
        "Low_Med": 3,
        "Med_High": 5,
        "High_Severe": 7,
        "Trace": 0,
        "Low": 2,
        "Med": 4,
        "High": 6,
        "Severe": 8
    }

    multi_part_severity_pattern = re.compile(r"(Trace_Low|Low_Med|Med_High|High_Severe)")

    def extract_pest_and_severity(code):
        if isinstance(code, str) and code.strip():
            multi_part_match = multi_part_severity_pattern.search(code)
            if multi_part_match:
                severity = severity_map[multi_part_match.group()]
            else:
                severity = None
            
            parts = code.split('_')

            pests = [part for part in parts if part not in severity_map and part != "" and part is not None]
            pests = pests if pests else [None]

            if severity is None:
                for part in parts:
                    if part in severity_map:
                        severity = severity_map[part]
                        break
        else:
            pests = [None]
            severity = None
        return pests, severity

    df['Pests'], df['Severity'] = zip(*df[code_col].apply(extract_pest_and_severity))

    # Expand DataFrame for multiple pests
    def expand_rows(df, col, new_col):
        temp_df = df.explode(col).reset_index(drop=True)
        temp_df[new_col] = temp_df[col]
        return temp_df.drop(columns=[col])

    df = expand_rows(df, 'Pests', 'Pest')

    basename = os.path.basename(pest_area_path)
    name, _ = os.path.splitext(basename)
    excel_path = os.path.join(out_dir, name + '_severity.xlsx')
    df.to_excel(excel_path)

# # ----------------------------- SORT BY DISTRICT ----------------------------- #

    severity_map = {
        0: "Trace",
        1: "Trace-Low",
        2: "Low",
        3: "Low-Moderate",
        4: "Moderate",
        5: "Moderate-High",
        6: "High",
        7: "High-Severe",
        8: "Severe"
    }

    df['Severity'] = df['Severity'].map(severity_map)

    new_df = df[[region_col,district_col, 'Pest', 'Severity', area_col]].copy()
    new_df.columns = ['Region', 'District', 'Pest', 'Severity', 'Area']

    summary_df = new_df.groupby(['Region', 'District', 'Pest', 'Severity'], as_index=False)['Area'].sum()

    total_area_df = new_df.groupby(['Region', 'District', 'Pest'], as_index=False)['Area'].sum()
    total_area_df['Severity'] = 'Total'

    final_df = pd.concat([summary_df, total_area_df], ignore_index=True)

    total_area_df['Area'] = total_area_df['Area'] / 10000
    total_area_df.columns = ['Region', 'District', 'Pest', 'Area (ha)', 'Severity']
    totals_path = os.path.join(out_dir, 'totals_only.xlsx')
    total_area_df.to_excel(totals_path, index=False)

    severity_order = ["Trace", "Trace-Low", "Low", "Low-Moderate", "Moderate", "Moderate-High", "High", "High-Severe", "Severe", "Total"]
    final_df['Severity'] = pd.Categorical(final_df['Severity'], categories=severity_order, ordered=True)
    final_df = final_df.sort_values(by=['District', 'Pest', 'Severity'])
    final_df['Area'] = final_df['Area'] / 10000  
    final_df.columns = ['Region', 'District', 'Pest', 'Severity', 'Area (ha)']

    basename = os.path.basename(pest_area_path)
    name, _ = os.path.splitext(basename)
    excel_path = os.path.join(out_dir, name + '_summary.xlsx')
    final_df.to_excel(excel_path, index=False)

# ------------------------ ADD TO PREVIOUS YEARS DATA ------------------------ #

    year = str(year)

    totals_24 = pd.read_excel(totals_path)
    totals_prev = pd.read_excel(final_pest_area_path)

    pest_names_map = {
        'SN': 'Sirex',
        'DNB': 'Dothistroma',
        'MPA' : 'Monterey pine aphid',
        'DIP': 'Diplodia',
        'AN': 'Animal damage'
    }

    totals_24['Pest'] = totals_24['Pest'].map(pest_names_map)
    totals_24 = totals_24[totals_24['Pest'].notna()]


    if year not in totals_prev.columns:
        totals_prev[year] = 0

    totals_prev[year] = totals_prev[year].astype(object)


    for index, row in totals_24.iterrows():
        district = row['District']
        pest = row['Pest']
        value = row['Area (ha)']
        
        # Strip leading/trailing spaces and ensure consistent casing for matching
        district = district.strip().replace(' ', '').lower()
        pest = pest.strip().lower()
        
        # totals_prev['District'] = totals_prev['District'].str.strip().str.lower()
        # totals_prev['Pest'] = totals_prev['Pest'].str.strip().str.lower()

        
        match = (totals_prev['District'].str.strip().str.lower() == district) & (totals_prev['Pest'].str.strip().str.lower() == pest)
        
        if match.any():
            totals_prev.loc[match, year] = round(value, 2)
    totals_prev['Region'] = totals_prev['Region'].str.capitalize()
    basename = os.path.basename(final_pest_area_path)
    name, _ = os.path.splitext(basename)
    excel_path = os.path.join(out_dir, name + f'_{year}.xlsx')
    totals_prev.to_excel(excel_path, index=False)

# ---------------------------------------------------------------------------- #
#                                     PLOTS                                    #
# ---------------------------------------------------------------------------- #


# ----------------- REGION - YEAR BY AREA FOR EACH PEST TYPE ----------------- #

    # import pandas as pd
    # import plotly.express as px

    # # Reading the excel file
    # df = totals_prev

    # # Filter data for Gippsland, Northern, and Western regions
    # regions = df['Region'].unique()
    # regions = [regions[0]]
    # df_filtered = df[df['Region'].isin(regions)]

    # # Function to plot data for a given region
    # def plot_region_data(region):
    #     df_region = df_filtered[df_filtered['Region'] == region]
    #     fig = px.bar(
    #         df_region.melt(id_vars=["Region", "District", "Pest"], var_name="Year", value_name="Count"),
    #         x="Year", y="Count", color="Pest", barmode="group",
    #         facet_col="District", title=f"Pest Count in {region} Region"
    #     )
    #     # fig.show()
    #     output_file = pp / f"airdata/pest_count_{region}_{district}.png"
    #     fig_combined.write_image(output_file)


    # # Generate plots for each region
    # for region in regions:
    #     plot_region_data(region)

# --------------------------- PLOTS FOR EACH REGION -------------------------- #

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # file_path = pp / 'airdata/final_2024.xlsx'
    df = totals_prev
    df = df.round(2)

    def plot_region_data(region):
        df_region = df[df['Region'] == region]
        df_melted = df_region.melt(id_vars=["Region", "District", "Pest"], var_name="Year", value_name="Count")
        df_region_summed = df_region.groupby(['Region', 'Pest']).sum().reset_index().round(2)

        fig = px.bar(
            df_melted,
            x="Pest", y="Count", color="Year", barmode="group",
            title=f"Pest Count in {region} Region"
        )

        table_data = df_region_summed.set_index(['Pest']).T.reset_index()
        table_data.columns = ['Year'] + [f'{pest}' for pest in table_data.columns[1:]]
        table_data = table_data[table_data['Year'].apply(lambda x: str(x).isdigit())]


        table_trace = go.Table(
            header=dict(values=list(table_data.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[table_data[col] for col in table_data.columns],
                    fill_color='lavender',
                    align='left')
        )

        fig_combined = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1, 
            specs=[[{"type": "xy"}], [{"type": "table"}]]
        )

        for trace in fig.data:
            fig_combined.add_trace(trace, row=1, col=1)

        fig_combined.add_trace(table_trace, row=2, col=1)
        fig_combined.update_layout(height=1000, title_text=f"Pest Count in {region} Region with Data Summary Table")

        output_file = os.path.join(out_dir, f"pest_count_{region}.png")
        fig_combined.write_image(output_file)

    # Generate plots for each region
    regions = df['Region'].unique()
    # regions= [regions[0]]
    for region in regions:
        plot_region_data(region)

# -------------------------- PLOTS FOR EACH DISTRICT ------------------------- #

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from pathlib import Path

    df = totals_prev
    df = df.round(2)

    def plot_district_data(region, district):
        df_district = df[(df['Region'] == region) & (df['District'] == district)]

        df_district_summed = df_district.groupby(['Region', 'District', 'Pest']).sum().reset_index()
        df_melted = df_district_summed.melt(id_vars=["Region", "District", "Pest"], var_name="Year", value_name="Count")

        fig = px.bar(
            df_melted,
            x="Pest", y="Count", color="Year", barmode="group",
            title=f"Pest Count in {district} District of {region} Region"
        )

        table_data = df_district_summed.set_index(['Pest']).T.reset_index()
        table_data.columns = ['Year'] + [f'{pest}' for pest in table_data.columns[1:]]
        
        table_data = table_data[table_data['Year'].apply(lambda x: str(x).isdigit())]

        table_trace = go.Table(
            header=dict(values=list(table_data.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[table_data[col] for col in table_data.columns],
                    fill_color='lavender',
                    align='left')
        )

        fig_combined = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1, 
            specs=[[{"type": "xy"}], [{"type": "table"}]]
        )

        for trace in fig.data:
            fig_combined.add_trace(trace, row=1, col=1)

        fig_combined.add_trace(table_trace, row=2, col=1)
        fig_combined.update_layout(height=1000, title_text=f"Pest Count in {district} District of {region} Region with Data Summary Table")

        # fig_combined.show()
        output_file =os.path.join(out_dir, f"pest_count_{region}_{district}.png")
        fig_combined.write_image(output_file)


    for district in df['District'].unique():
        region = df[df['District'] == district]['Region'].values[0]
        plot_district_data(region, district)

