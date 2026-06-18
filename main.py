import sys
import os
from pathlib import Path

from src.profiel_model import process_profiles
from src.profiel_grafiek import generate_profile_graphs
from src.profiel_dimensionering import generate_profile_dimensions
from src.pdf_generator import generate_pdf

PROFILES_FOLDER = Path("data/Merwede_Profiles")
DEFAULT_EV_COUNT = 167
DEFAULT_COS_PHI = 0.9


def run_pipeline(ev_count: int, cos_phi: float):
    profile_df_dict = process_profiles(
        profiles_folder=PROFILES_FOLDER,
        vehicle_count=ev_count,
        cos_phi=cos_phi
    )

    profile_graph_dict = generate_profile_graphs(profile_df_dict)
    
    profile_graph_dict = generate_profile_dimensions(
        profile_df_dict, cos_phi, profile_graph_dict
    )
    
    return profile_df_dict, profile_graph_dict


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    mode = sys.argv[1] if len(sys.argv) > 1 else "main"
    ev_count = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_EV_COUNT
    cos_phi = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_COS_PHI

    print(f"Running mode: {mode}")
    print(f"EV count     = {ev_count}")
    print(f"cos_phi      = {cos_phi}")

    profile_df_dict, profile_graph_dict = run_pipeline(ev_count, cos_phi)

    if mode == "pdf":
        generate_pdf(profile_graph_dict, ev_count, cos_phi)
    else:
        print("Main() uitgevoerd — geen PDF gemaakt.")
        
    return profile_df_dict, profile_graph_dict


if __name__ == "__main__":
    profile_df_dict, profile_graph_dict = main()