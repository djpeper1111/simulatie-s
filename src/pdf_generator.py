from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os 
from main import main

def generate_graphs_only():
    # 1. Output map aanmaken
    output_map = "output"
    os.makedirs(output_map, exist_ok=True)

    # 2. Pad naar PDF
    pdf_path = os.path.join(output_map, "Merwede_Profiles.pdf")

    # 3. Haal grafieken op uit main.py
    graphs = main()   # main() moet return graphs hebben!

    # 4. PDF genereren
    with PdfPages(pdf_path) as pdf:

        # Titelpagina
        fig = plt.figure(figsize=(10, 6))
        plt.text(
            0.5, 0.5,
            "Merwede energieprofiel Rapport",
            ha='center', va='center', fontsize=28
        )
        pdf.savefig(fig)
        plt.close(fig)
        
        # Alle grafieken toevoegen
        for name, fig in graphs.items():
            pdf.savefig(fig)
            plt.close(fig)

    print("PDF opgeslagen in:", pdf_path)
