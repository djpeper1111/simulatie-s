# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:47:58 2026

@author: Luuk
"""
#import 
from src.Merwede_Model import generate_graphs, get_profile_df
from pdf_generator import generate_pdf
from pathlib import Path


ev_count = 200
profiles_folder = Path("data/Merwede_Profiles")


def generate_graphs_only():
    graphs = generate_graphs(
        get_profile_df(ev_count, profiles_folder)
    )
    return graphs

def generate_pdf_report():
    generate_pdf()

def compleet():
    generate_graphs_only()
    generate_pdf_report()

if __name__ == "__main__":
    pass