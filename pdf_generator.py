from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os

def generate_pdf(graphs):
    output_map = "output_pdf"
    os.makedirs(output_map, exist_ok=True)
    pdf_path = os.path.join(output_map, "Merwede_Profiles.pdf")

    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Merwede energieprofiel Rapport",
                 ha='center', va='center', fontsize=28)
        pdf.savefig(fig)
        plt.close(fig)

        for name, fig in graphs.items():
            pdf.savefig(fig)
            plt.close(fig)

    print("PDF opgeslagen in:", pdf_path)