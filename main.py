# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:47:58 2026

@author: Luuk
"""

from src.Merwede_Model import generate_graphs

from pathlib import Path


ev_count = 200
profiles_folder = Path("data/Merwede_Profiles")

def main():
    generate_graphs(ev_count, profiles_folder)
    
    
if __name__ == "__main__":
    main()

    # test test