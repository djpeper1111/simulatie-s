# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 16:38:33 2026

@author: Luuk
"""
import pandas as pd

number_ms_trafos = 3
number_ls_trafos_per_ms_trafos = 4

def generate_profile_dimensions(profile_df_dict):
    # 4 dimensions per profile (without V2G (without n-1, with n-1), with V2G (without n-1, with n-1))
    dimensions = ["No V2G, No N-1", "No V2G, N-1", "V2G, No N-1", "V2G, N-1"]
    
    for clean_key, data_dict in profile_df_dict.items():
        dimension_metrics = []
        
        for dimension in dimensions:
            dimension_metrics.append({
                "Dimension": dimension,
                "Average_kVA": 0,
                "Max_kVA": 0,
                "Difference_Min-Max_kVA": 0,
                "kVA_per_MS_trafo": 0,
                "kVA_per_LS_trafo": 0
            })
            
        profile_df_dict[clean_key]["dimensions"] = pd.DataFrame(dimension_metrics)
            
    return profile_df_dict