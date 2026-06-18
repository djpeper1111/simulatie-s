import sys
import os
from pathlib import Path

from src.profiel_model import process_profiles
from src.profiel_grafiek import generate_profile_graphs
from src.profiel_dimensionering import generate_profile_dimensions
from src.pdf_generator import generate_pdf

os.chdir(os.path.dirname(os.path.abspath(__file__)))

profiles_folder = Path("data/Merwede_Profiles")

ev_count = 200
cos_phi = 0.9

if len(sys.argv) >= 4:
    # sys.argv[1] = command (pdf/update)
    ev_count = int(sys.argv[2])
    cos_phi = float(sys.argv[3])

print("EV count =", ev_count)
print("cos_phi =", cos_phi)


def pdf():
    
    
    profile_df_dict = process_profiles(
        profiles_folder=profiles_folder,
        vehicle_count=ev_count,
        cos_phi=cos_phi
    )

    profile_graphs = generate_profile_graphs(profile_df_dict)

    profile_graphs = generate_profile_dimensions(
        profile_df_dict, cos_phi, profile_graphs
    )

    generate_pdf(profile_graphs, ev_count, cos_phi)

    print("PDF succesvol gegenereerd.")

def main():
    profile_df_dict = process_profiles(
        profiles_folder=profiles_folder,
        vehicle_count=ev_count,
        cos_phi=cos_phi
    )

    profile_graph_dict = generate_profile_graphs(profile_df_dict)

    profile_graph_dict = generate_profile_dimensions(
        profile_df_dict, cos_phi, profile_graph_dict
    )

    print("Main() uitgevoerd — geen PDF gemaakt.")
    return profile_df_dict, profile_graph_dict


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "pdf":
        pdf()
    else:
        profile_df_dict, profile_graph_dict = main()