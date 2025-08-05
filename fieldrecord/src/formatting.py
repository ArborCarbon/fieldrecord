from tqdm import tqdm
import numpy as np
import pandas as pd

def format_codes(df, SEVERITY_MAP, ABIOTIC_MAP, PEST_MAP, SEVERITY_RANK,):

    _map = {**SEVERITY_MAP, **ABIOTIC_MAP, **PEST_MAP,}

    def get_maps(x, _map):
        formatted = {}
        for k, v in x.items():
            if k == 'no-severity':
                formatted['no-severity'] = v
            
            if k in _map.keys():
                formatted[_map[k]] = v
        for k, v in formatted.items():

            n = [_map[severity] for severity in v if severity in _map.keys()]
            formatted[k] = n
        return formatted
    
    def apply_format(df, _map):
        df['CODE_dict'] = df['CODE_dict'].apply(lambda x: get_maps(x, _map))
        return df
    
    df = apply_format(df, _map)

    return df
    
def put_codes_in_columns(df, columns_to_process, ABIOTIC_MAP, PEST_MAP, SEVERITY_RANK):

    def get_main_pests(x, mp_col, mp_code):
        if mp_code in x['CODE_dict'].keys():
            severity = x['CODE_dict'][mp_code]
            if not severity:
                severity = ['Trace']
            x[mp_col] = "-".join(severity)
            # x['CODE_dict'].pop(mp_code) # check
            return x
        else:
            x[mp_col] = None # ir
            return x

    def get_severity(x, pests, SEVERITY_RANK):
        severity_value = None
        severity_abiotic_value = None
        severity_pest_value = None
        SEVERITY_UNRANK = {value: key for key, value in SEVERITY_RANK.items()}

        # calculate max total severity 
        severity = [x['CODE_dict'][pest] for pest in pests]
        severity = ["-".join(s) for s in severity if s]
        if severity:
            severity_ranked = [SEVERITY_RANK[severity] for severity in severity]
            max_severity = max(severity_ranked)
            severity_value = SEVERITY_UNRANK[max_severity]

        # calculate max abiotic severity 
        severity_abiotic = [x['CODE_dict'][pest] for pest in pests if pest in ABIOTIC_MAP.keys()]
        severity_abiotic = ["-".join(s) for s in severity_abiotic if s]
        if severity_abiotic:
            severity_abiotic_ranked = [SEVERITY_RANK[severity] for severity in severity_abiotic]
            max_severity_abiotic = max(severity_abiotic_ranked)
            severity_abiotic_value = SEVERITY_UNRANK[max_severity_abiotic]

        # calculate max pest severity 
        severity_pest = [x['CODE_dict'][pest] for pest in pests if pest in PEST_MAP.values()]
        severity_pest = ["-".join(s) for s in severity_pest if s]
        if severity_pest:
            severity_pest_ranked = [SEVERITY_RANK[severity] for severity in severity_pest]
            max_severity_pest = max(severity_pest_ranked)
            severity_pest_value = SEVERITY_UNRANK[max_severity_pest]
        
        return severity_value, severity_pest_value, severity_abiotic_value

    def get_other_pests(x, other_col, _map, SEVERITY_RANK):
        other_pests = [k for k in x['CODE_dict'].keys() if k in _map.values()]
        empty_pest = [k for k in x['CODE_dict'].keys() if k == 'no-severity']

        if other_pests:
            x[other_col] = "-".join(other_pests)
            # x['Severity'] = get_severity(x, other_pests, SEVERITY_RANK)
            s, s_pest, s_abiotic = get_severity(x, other_pests, SEVERITY_RANK)
            if pd.isna(x.get('Severity')) or x.get('Severity') is None:
                x['Severity'] = s
            else:
                old_s = x.get('Severity')
                if SEVERITY_RANK[s] > SEVERITY_RANK[old_s]:
                    x['Severity'] = s
            if pd.isna(x.get('Severity_Pest')) or x.get('Severity_Pest') is None:
                x['Severity_Pest'] = s_pest
            if pd.isna(x.get('Severity_Abiotic')) or x.get('Severity_Abiotic') is None:
                x['Severity_Abiotic'] = s_abiotic
            # Add this just once after processing the DataFrame row-wise
            return x
        elif empty_pest:
            x[other_col] = None # ir
            # x['Severity'] = get_severity(x, empty_pest, SEVERITY_RANK)
            s, s_pest, s_abiotic = get_severity(x, other_pests, SEVERITY_RANK)
            if pd.isna(x.get('Severity')) or x.get('Severity') is None:
                x['Severity'] = s
            if pd.isna(x.get('Severity_Pest')) or x.get('Severity_Pest') is None:
                x['Severity_Pest'] = s_pest
            if pd.isna(x.get('Severity_Abiotic')) or x.get('Severity_Abiotic') is None:
                x['Severity_Abiotic'] = s_abiotic
            return x
        else:
            x[other_col] = None # ir
            return x

    def apply_main_pests(df, mp_col, mp_code):
        df = df.apply(lambda x: get_main_pests(x, mp_col, mp_code), axis=1)
        return df
             
    def apply_other_pests(df, other_col, _map, SEVERITY_RANK):
        df = df.apply(lambda x: get_other_pests(x, other_col, _map, SEVERITY_RANK), axis=1)
        return df

    for col, code in columns_to_process.items():
        if col not in ["Abiotic2025", "PestD_2025"]:
            df = apply_main_pests(df, col, code)
        elif col == "Abiotic2025":
            df = apply_other_pests(df, col, ABIOTIC_MAP, SEVERITY_RANK)
        elif col == "PestD_2025":
            df = apply_other_pests(df, col, PEST_MAP, SEVERITY_RANK)
        
    if 'Severity' not in df.columns:
        df['Severity'] = None # ir
        df['Severity_Pest'] = None # ir
        df['Severity_Abiotic'] = None # ir

    return df
     
def merge_duplicates(df, severity_rank):
    # df_sorted = df.sort_values('GlobalID') 
    # df_sorted=df[(df['GlobalID']=='{4354F319-6ABA-41ED-A911-9DC6A333B984}') | (df['GlobalID']=='{DF1E2C43-255E-4F05-ADAB-0AEC76C54F95}')]
    grouped = df.groupby('GlobalID')

    to_remove=[]

    for global_id, group in grouped: 
        if len(group) > 1:
            # add all idx except first to to_remove
            to_remove.extend(group.index[1:])
            
            # make the first in the group's CODE_dict a list of all the codes in the group
            df.at[group.index[0], 'CODE'] = ','.join(map(str, group['CODE'].values))

            # combine all the code dictionaries, keeping the highest severity value in cases of duplicate keys 
            combined_dict = {}
            for d in group['CODE_dict']:
                for k, v in d.items():
                    if k not in combined_dict:
                        combined_dict[k] = v
                    else:
                        # Keep the value with the highest severity (if it has a severity)
                        if v != [None]:
                            if combined_dict[k][0] not in severity_rank:
                                combined_dict[k] = v
                            else:
                                if severity_rank[v[0]] > severity_rank[combined_dict[k][0]]:
                                    combined_dict[k] = v
                        # if severity_rank[v[0]] > severity_rank[combined_dict[k][0]]:
                        #     combined_dict[k] = v
            df.at[group.index[0], 'CODE_dict'] = combined_dict
        
    # remove duplicates
    df_final = df.drop(to_remove)
    df_final.reset_index(drop=True, inplace=True)
    return(df_final)


        
# def sort_output_columns(df, input_cols, columns_to_process):
#     cols_to_keep =  input_cols + list(columns_to_process.keys()) + ['CODE', 'p_area','Severity','obs_idx' ]
#     df = df[cols_to_keep]
#     return df

def sort_output_columns(df, input_cols, columns_to_process):
    cols_to_keep = input_cols + list(columns_to_process.keys()) + ['CODE', 'p_area', 'Severity', 'Severity_Pest', 'Severity_Abiotic', 'obs_idx']
    if 'geometry' in cols_to_keep:
        cols_to_keep.remove('geometry')
    if 'geometry' in df.columns:
        cols_to_keep.append('geometry')
    df = df[cols_to_keep]
    return df

