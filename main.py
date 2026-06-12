from src.Merwede_Model import generate_graphs, get_profile_df
from pdf_generator import generate_pdf
from pathlib import Path
import sys

ev_count = 200
profiles_folder = Path("data/Merwede_Profiles")

def generate_graphs_only():
    graphs = generate_graphs(get_profile_df(ev_count, profiles_folder))
    return graphs

def generate_pdf_report():
    graphs = generate_graphs_only()
    generate_pdf(graphs)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "generate_graphs_only":
            generate_graphs_only()
        elif cmd == "generate_pdf_report":
            generate_pdf_report()
