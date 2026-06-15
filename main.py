# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:47:58 2026

@author: Luuk
"""

from src.merwede_model import process_profiles
from src.merwede_grafiek import generate_graphs

from pathlib import Path

ev_count = 167      
profiles_folder = Path("data/Merwede_Profiles")

def main():
    return (
        generate_graphs(
            process_profiles(
                profiles_folder=profiles_folder,
                vehicle_count=ev_count
            )
        ), 
        process_profiles(
            profiles_folder=profiles_folder,
            vehicle_count=ev_count
        )
    )
    
if __name__ == "__main__":
   profile_graph_dict, profile_df_dict = main()