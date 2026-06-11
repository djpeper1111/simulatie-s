# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 10:14:35 2026

@author: Luuk
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def scale_vehicles_series(
        df, 
        new_count, 
        base_count = 167
    ):
    df_copy = df.copy()
    
    if "vehicles" in df_copy.columns:
        factor = new_count / base_count
        df_copy["vehicles"] = df_copy["vehicles"] * factor
    
    return df_copy

def get_profile_df(
        new_vehicle_count,
        profiles_folder
    ):
    profile_df_dict = {}
    
    for file_path in profiles_folder.glob("*.csv"):
        clean_key = file_path.stem.split(" - ")[-1]
        df = pd.read_csv(file_path).set_index("time")
        
        profile_df_dict[clean_key] = scale_vehicles_series(df, new_vehicle_count)
        
    return profile_df_dict

def generate_graphs(
        profile_df_dict
    ):
    graphs = {}

    for profile_key, profile_df in profile_df_dict.items():
        graph, ax = plt.subplots(figsize=(10, 6))

        profile_df.plot.area(ax=ax, alpha=0.75)
        
        # get all the complete hours, the first of every 4 rows
        tick_intervals = np.arange(0, len(profile_df), 4)
        # get the first 5 charachters from the hour, at the tick_intervals
        tick_labels = [profile_df.index[pos][:5] for pos in tick_intervals]
        
        ax.set_xticks(tick_intervals)
        ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=9)
        
        ax.set_ylim(0, 7000)
        ax.set_title(profile_key, fontsize=14, fontweight="bold")
        ax.set_xlabel("Hours", fontsize=12, fontweight="bold")
        ax.set_ylabel("kW", fontsize=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)

        graphs[profile_key] = graph
    
    return graphs