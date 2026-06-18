# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 16:38:33 2026

@author: Luuk
"""
import pandas as pd
import numpy as np

from pathlib import Path
import matplotlib.pyplot as plt
import math

cables_csv = Path("data/Possible_Cables.csv")
trafos_csv = Path("data/Possible_Trafos.csv")

number_ms_trafos = 3
number_ls_trafos = 12
number_ls_trafos_per_ms_trafo = 4
number_connections_per_ls_trafo = 3
U_ms = 10000 # V
U_ls = 400 # V

def generate_profile_dimensions(profile_df_dict, cos_phi, profile_graph_dict):
    dimensions = ["No V2G, No N-1", "No V2G, N-1", "V2G, No N-1", "V2G, N-1"]
    
    for clean_key, data_dict in profile_df_dict.items():
        profile = data_dict["profile"]
        dimension_metrics = []
        
        for dimension in dimensions:
            temp_profile = profile.copy()
            
            if dimension.startswith("V2G"):
                temp_profile["Total_[kW]"] = np.minimum(temp_profile["Total_[kW]"], temp_profile["Limit_[kW]"])
                temp_profile["Total_[kVA]"] = temp_profile["Total_[kW]"] / cos_phi
            
            Max_kVA = temp_profile["Total_[kVA]"].max()
            Avg_kVA = temp_profile["Total_[kVA]"].mean()
            Min_kVA = temp_profile["Total_[kVA]"].min()
            
            is_n_minus_1 = "No N-1" not in dimension
            
            ms_trafos_available = number_ms_trafos - 1 if is_n_minus_1 else number_ms_trafos
            kVA_per_MS_trafo = Max_kVA / ms_trafos_available
            
            ls_trafos_lost = number_ls_trafos / number_ls_trafos_per_ms_trafo if is_n_minus_1 else 0
            ls_trafos_available = number_ls_trafos - ls_trafos_lost
            kVA_per_LS_trafo = Max_kVA / ls_trafos_available
            
            dimension_metrics.append({
                "Dimension": dimension,
                "Average_kVA": Avg_kVA,
                "Max_kVA": Max_kVA,
                "Difference_Min-Max_kVA": Max_kVA - Min_kVA,
                "kVA_per_MS_trafo": kVA_per_MS_trafo,
                "kVA_per_LS_trafo": kVA_per_LS_trafo,
                "MS_kA": kVA_per_MS_trafo / (math.sqrt(3) * U_ms),
                "LS_kA": (kVA_per_LS_trafo / (math.sqrt(3) * U_ls)) / number_connections_per_ls_trafo
            })
            
        profile_df_dict[clean_key]["dimensions"] = pd.DataFrame(dimension_metrics)
        
        profile_graph_dict[clean_key]["dimension"] = plot_asset_specifications(
            select_assets(profile_df_dict[clean_key]["dimensions"]),
            clean_key
        )
            
    return profile_graph_dict


def select_assets(dimension_metrics):
    cables_df = pd.read_csv(cables_csv).set_index("Kabel_ID")
    trafos_df = pd.read_csv(trafos_csv).set_index("Trafo_ID")
    
    ms_trafos = trafos_df[trafos_df["Type"] == "Substation"].sort_values("Vermogen_kVA")
    ls_trafos = trafos_df[trafos_df["Type"] == "Wijk"].sort_values("Vermogen_kVA")
    
    ms_cables = cables_df[cables_df["Netvlak"] == "Middenspanning (MS)"].sort_values(
        by=["Geleider_Materiaal", "Max_Amperage_A"], 
        ascending=[True, True]
    )
    ls_cables = cables_df[cables_df["Netvlak"] == "Laagspanning (LS)"].sort_values(
        by=["Geleider_Materiaal", "Max_Amperage_A"], 
        ascending=[True, True]
    )
    
    assets = []
    for _, dimension_metric in dimension_metrics.iterrows():
        asset = {}
        dim = dimension_metric["Dimension"]
        asset["dimension"] = dim
        is_n1 = "No N-1" not in dim
        
        ms_trafo = ms_trafos[ms_trafos["Vermogen_kVA"] >= dimension_metric["kVA_per_MS_trafo"]].iloc[0]
        ls_trafo = ls_trafos[ls_trafos["Vermogen_kVA"] >= dimension_metric["kVA_per_LS_trafo"]].iloc[0]
        
        asset["trafo_rows"] = [
            [
                "MS Transformator",
                f"Primair: {ms_trafo['Primaire_kV']} kV\nSecundair: {ms_trafo['Secundaire_kV']} kV\nGrens: {ms_trafo['Vermogen_kVA']} kVA",
                f"Schakeling: {ms_trafo['Schakeling']}\nKorstluitspanning: {ms_trafo['Kortsluitspanning_Procent']}%\nKortsluitverlies: {ms_trafo['Kortsluitverlies_W']} W",
                f"B: {ms_trafo['Breedte_mm']} mm\nL: {ms_trafo['Lengte_mm']} mm\nH: {ms_trafo['Hoogte_mm']} mm",
                number_ms_trafos
            ],
            [
                "LS Transformator",
                f"Primair: {ls_trafo['Primaire_kV']} kV\nSecundair: {ls_trafo['Secundaire_kV']} kV\nGrens: {ls_trafo['Vermogen_kVA']} kVA",
                f"Schakeling: {ls_trafo['Schakeling']}\nKorstluitspanning: {ls_trafo['Kortsluitspanning_Procent']}%\nKortsluitverlies: {ls_trafo['Kortsluitverlies_W']} W",
                f"B: {ls_trafo['Breedte_mm']} mm\nL: {ls_trafo['Lengte_mm']} mm\nH: {ls_trafo['Hoogte_mm']} mm",
                number_ls_trafos
            ]
        ]
        
        ms_amps = dimension_metric["MS_kA"] * 1000
        ms_cable = ms_cables[ms_cables["Max_Amperage_A"] >= ms_amps].iloc[0]
        ms_res_total = ms_cable["Weerstand_Ohm_km"] * (ms_cable["Lengte_Indicatie_m"] / 1000.0)
        ms_v_drop = math.sqrt(3) * ms_amps * ms_res_total
        
        ls_amps = dimension_metric["LS_kA"] * 1000
        ls_cable = ls_cables[ls_cables["Max_Amperage_A"] >= ls_amps].iloc[0]
        ls_res_total = ls_cable["Weerstand_Ohm_km"] * (ls_cable["Lengte_Indicatie_m"] / 1000.0)
        ls_v_drop = math.sqrt(3) * ls_amps * ls_res_total
        
        asset["cable_rows"] = [
            [
                "MS Cable",
                f"Spanning: {ms_cable['Spanningsniveau_kV']} kV\nMateriaal: {ms_cable['Geleider_Materiaal']}",
                f"Doorsnede: {ms_cable['Doorsnede_mm2']} mm²\nAder Aantal: {ms_cable['Aantal_Aders']}",
                f"Max Amperage: {ms_cable['Max_Amperage_A']} A\nWeerstand: {ms_cable['Weerstand_Ohm_km']} Ω/km\nSpanningsval: {ms_v_drop:.1f} V",
                "2 per Trafo" if is_n1 else "1 per Trafo"
            ],
            [
                "LS Cable",
                f"Spanning: {ls_cable['Spanningsniveau_kV']} kV\nMateriaal: {ls_cable['Geleider_Materiaal']}",
                f"Doorsnede: {ls_cable['Doorsnede_mm2']} mm²\nAder Aantal: {ls_cable['Aantal_Aders']}",
                f"Max Amperage: {ls_cable['Max_Amperage_A']} A\nWeerstand: {ls_cable['Weerstand_Ohm_km']} Ω/km\nSpanningsval: {ls_v_drop:.1f} V",
                "6 per Trafo" if is_n1 else "3 per Trafo"
            ]
        ]
        
        assets.append(asset)
        
    return assets

def plot_asset_specifications(assets_list, profile_title):
    # 4 subplots total: One per dimension card block
    fig, axes = plt.subplots(4, 1, figsize=(15, 18))
    fig.suptitle(f"Profiel: {profile_title}", fontsize=22, fontweight='bold', color='black', y=1.02)
    
    trafo_headers = ["Categorie", "Spanning & Grens", "Parameters", "Afmetingen (B x L x H)", "Aantal"]
    cable_headers = ["Categorie", "Spanning & Materiaal", "Doorsnede & Aders", "Parameters & Spanningsval", "Kabels per Trafo"]
    
    for idx, asset in enumerate(assets_list):
        dimension_name = asset["dimension"]
        ax = axes[idx]
        ax.axis('off')
        
        # 1. Clean, independent dimension title
        ax.text(0, 1.2, f"Dimensie: {dimension_name}", fontsize=15, fontweight='bold', color='black', transform=ax.transAxes)
        
        # 2. Transformer Table 
        # bbox layout: starts at vertical height 0.52, extends up to 0.97. Total height is 0.45 of the room.
        t_table = ax.table(
            cellText=asset["trafo_rows"], 
            colLabels=trafo_headers, 
            cellLoc='left', 
            colWidths=[0.125, 0.25, 0.25, 0.25, 0.125],
            bbox=[0, 0.6, 1.0, 0.55]
        )
        t_table.auto_set_font_size(False)
        t_table.set_fontsize(11.5) # Made font slightly bigger too!
        
        for col in range(5):
            t_table[0, col].set_text_props(weight='bold', color='white')
            t_table[0, col].set_facecolor('#1e3a5f')
            
        # 3. Cable Table
        # bbox layout: starts at vertical height 0.0, extends up to 0.45. Total height is 0.45.
        # This leaves an intentional, exact gap of 0.07 between them (0.52 - 0.45)
        c_table = ax.table(
            cellText=asset["cable_rows"], 
            colLabels=cable_headers, 
            cellLoc='left', 
            colWidths=[0.125, 0.25, 0.25, 0.25, 0.125],
            bbox=[0, 0.0, 1.0, 0.55]
        )
        c_table.auto_set_font_size(False)
        c_table.set_fontsize(11.5)
        
        for col in range(5):
            c_table[0, col].set_text_props(weight='bold', color='white')
            c_table[0, col].set_facecolor('#2e5a36')
            
    # 4. Global spacing controls
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.35) # Controls space between the 4 major dimension blocks
    
    plt.close(fig)
    return fig