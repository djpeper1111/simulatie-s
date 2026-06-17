# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 16:38:33 2026

@author: Luuk
"""
import pandas as pd
import numpy as np
import math

number_ms_trafos = 3
number_ls_trafos = 12
number_connections_per_ms_trafo = 4
number_connections_per_ls_trafo = 3
U_ms = 10000 # V
U_ls = 400 # V

def generate_profile_dimensions(profile_df_dict, cos_phi):
    dimensions = ["No V2G, No N-1", "No V2G, N-1", "V2G, No N-1", "V2G, N-1"]
    
    for clean_key, data_dict in profile_df_dict.items():
        profile = data_dict["profile"]
        dimension_metrics = []
        
        for dimension in dimensions:
            temp_profile = profile.copy()
            
            if dimension.startswith("V2G"):
                temp_profile["Total_[kW]"] = np.minimum(temp_profile["Total_[kW]"], temp_profile["Limit_[kW]"])
                temp_profile["Total_[kVA]"] = temp_profile["Total_[kW]"] / cos_phi
            
            Max_kVA = temp_profile["Total_[kVA]"].max()
            Avg_kVA = temp_profile["Total_[kVA]"].mean()
            Min_kVA = temp_profile["Total_[kVA]"].min()
            
            is_n_minus_1 = "No N-1" not in dimension
            
            ms_trafos_available = number_ms_trafos - 1 if is_n_minus_1 else number_ms_trafos
            kVA_per_MS_trafo = Max_kVA / ms_trafos_available
            
            ls_trafos_lost = number_ls_trafos / number_connections_per_ms_trafo if is_n_minus_1 else 0
            ls_trafos_available = number_ls_trafos - ls_trafos_lost
            kVA_per_LS_trafo = Max_kVA / ls_trafos_available
            
            dimension_metrics.append({
                "Dimension": dimension,
                "Average_kVA": Avg_kVA,
                "Max_kVA": Max_kVA,
                "Difference_Min-Max_kVA": Max_kVA - Min_kVA,
                "kVA_per_MS_trafo": kVA_per_MS_trafo,
                "kVA_per_LS_trafo": kVA_per_LS_trafo,
                "MS_kA": kVA_per_MS_trafo / (math.sqrt(3) * U_ms),
                "LS_kA": (kVA_per_LS_trafo / (math.sqrt(3) * U_ls)) / number_connections_per_ls_trafo
            })
            
        profile_df_dict[clean_key]["dimensions"] = pd.DataFrame(dimension_metrics)
            
    return profile_df_dict