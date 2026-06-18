from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os

def generate_pdf(graphs, ev_count, cos_phi):
    output_map = "output"
    os.makedirs(output_map, exist_ok=True)

    for profile_name, graph in graphs.items():
        print(f"Generating PDF for {profile_name}...")

        filename = f"{profile_name}_EvCount-{ev_count}_CosPhi-{cos_phi}.pdf"
        pdf_path = os.path.join(output_map, filename)

        with PdfPages(pdf_path) as pdf:
            for graph_name, fig in graph.items():

                temp_path = "temp_fig.png"
                fig.savefig(temp_path, dpi=300, bbox_inches="tight")
                plt.close(fig)

                img = plt.imread(temp_path)
                img_h, img_w = img.shape[0], img.shape[1]
                img_ratio = img_w / img_h

                a4_w, a4_h = 8.27, 11.69
                a4_ratio = a4_w / a4_h

                a4_fig = plt.figure(figsize=(a4_w, a4_h))

                if img_ratio > a4_ratio:
                    display_w = 0.9
                    display_h = display_w / img_ratio
                else:
                    display_h = 0.9
                    display_w = display_h * img_ratio

                left = (1 - display_w) / 2
                bottom = (1 - display_h) / 2

                ax = a4_fig.add_axes([left, bottom, display_w, display_h])
                ax.imshow(img)
                ax.axis("off")

                pdf.savefig(a4_fig)
                plt.close(a4_fig)

                os.remove(temp_path)

        print("PDF OPGESLAGEN", pdf_path)
