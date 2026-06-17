# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:47:58 2026

@author: Luuk
"""

from src.profiel_model import process_profiles
from src.profiel_grafiek import generate_profile_graphs
from src.profiel_dimensionering import generate_profile_dimensions
from src.pdf_generator import generate_pdf
from pathlib import Path
import sys

profiles_folder = Path("data/Merwede_Profiles")

ev_count = 167
cos_phi = 0.9

def pdf():
    # pdfs maken van profile_graph_dict
    return

def main():
   profile_df_dict = process_profiles(
        profiles_folder=profiles_folder,
        vehicle_count=ev_count,
        cos_phi=cos_phi
   )
   
   profile_graph_dict = generate_profile_graphs(
       profile_df_dict
   )
   
   return (
       profile_df_dict,
       
       generate_profile_dimensions(
            profile_df_dict, cos_phi, profile_graph_dict
       )
    )
    
if __name__ == "__main__":
   profile_df_dict, profile_graph_dict = main()