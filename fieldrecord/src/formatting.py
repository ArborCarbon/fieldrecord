


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
    
def put_codes_in_columns(df, columns_to_process, SEVERITY_RANK):

    def get_main_pests(x, mp_col, mp_code):
        if mp_code in x['CODE_dict'].keys():
            severity = x['CODE_dict'][mp_code]
            if not severity:
                severity = ['Trace']
            x[mp_col] = "-".join(severity)
            x['CODE_dict'].pop(mp_code)
            return x
        else:
            x[mp_col] = ''
            return x


    def get_severity(x, pests, SEVERITY_RANK):
        severity = [x['CODE_dict'][pest] for pest in pests]
        severity = ["-".join(s) for s in severity if s]
        if severity:
            severity_ranked = [SEVERITY_RANK[severity] for severity in severity]
            max_severity = max(severity_ranked)
            SEVERITY_UNRANK = {value: key for key, value in SEVERITY_RANK.items()}
            return SEVERITY_UNRANK[max_severity]
        
    def get_other_pests(x, other_col, _map, SEVERITY_RANK):
        other_pests = [k for k in x['CODE_dict'].keys() if k in _map.values()]
        empty_pest = [k for k in x['CODE_dict'].keys() if k == 'no-severity']
        if other_pests:
            x[other_col] = "-".join(other_pests)
            x['Severity'] = get_severity(x, other_pests, SEVERITY_RANK)
            return x
        elif empty_pest:
            x[other_col] = ''
            x['Severity'] = get_severity(x, empty_pest, SEVERITY_RANK)
            return x
        else:
            x[other_col] = ''
            return x


    def apply_main_pests(df, mp_col, mp_code):
        df = df.apply(lambda x: get_main_pests(x, mp_col, mp_code), axis=1)
        return df
             
    def apply_other_pests(df, other_col, _map, SEVERITY_RANK):
        df = df.apply(lambda x: get_other_pests(x, other_col, _map, SEVERITY_RANK), axis=1)
        return df

    for col, code in columns_to_process.items():
        if isinstance(code, str):
            df = apply_main_pests(df, col, code)
            
    for col, _map in columns_to_process.items():
        if isinstance(_map, dict):
            df = apply_other_pests(df, col, _map, SEVERITY_RANK)

    
    df['Severity'] = df['Severity'].fillna('')

    return df
        
        
        
def sort_output_columns(df, input_cols, columns_to_process):
    cols_to_keep =  input_cols + list(columns_to_process.keys()) + ['CODE', 'p_area','Severity','obs_idx' ]
    df = df[cols_to_keep]
    return df