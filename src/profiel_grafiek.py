# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 14:46:00 2026

@author: Luuk
"""

import matplotlib.pyplot as plt

COLUMN_MAPPING = {
    "homeappliances": "Homeappliances_[kW]",
    "utilities": "Utilities_[kW]",
    "heating": "Heating_[kW]",
    "water": "Water_[kW]",
    "vehicles": "Vehicles_[kW]"
}

GRID_LABLE_MAPPING = {
    "Peak_ID": "Peak",
    "Start_Time": "Start",
    "Stop_Time": "End",
    "Car_Count": "Cars Needed",
    "Total_[kWh]": "Energy [kWh]",
    "Min_Average_Battery_[%]": "Min Avg Battery [%]"
}

def generate_profile_graphs(profile_df_dict: dict) -> dict:
    """Iterates through profiles and generates a combined figure for each."""
    profile_graph_dict = {}
    
    for profile_key, data_dict in profile_df_dict.items():
        profile_graph_dict[profile_key] = {}
        
        fig = _plot_single_profile(
            profile_key, 
            data_dict["profile"], 
            data_dict["excess"], 
            data_dict["metrics"]
        )
        profile_graph_dict[profile_key]["profile"] = fig
        
    return profile_graph_dict


def _plot_single_profile(profile_key, df, excess_df, metrics_df):
    """Handles the creation and layout of a single figure."""
    # Balanced 10x10 square canvas with explicit room allocated between plots
    fig, (ax1, ax2) = plt.subplots(
        2, 1, 
        figsize=(10, 10), 
        sharex=True
    )
    
    # Clean manual spacing adjustments: leaves a wide margin at the bottom for the table
    fig.subplots_adjust(top=0.93, bottom=0.25, hspace=0.12)
    
    # Calculate global X-ticks
    tick_intervals = list(range(0, len(df), 4))
    tick_labels = [str(df.index[pos])[:5] for pos in tick_intervals]
    
    # ---- TOP PLOT: Profile ----
    available_cols = [c for c in COLUMN_MAPPING.values() if c in df.columns]
    df[available_cols].plot.area(ax=ax1, alpha=0.75)
    
    if "Limit_[kW]" in df.columns:
        ax1.axhline(y=df["Limit_[kW]"].iloc[0], color="red", linestyle=":", linewidth=1.5, label="Limit")
        
    if "Total_[kW]" in df.columns:
        ax1.plot(df.index, df["Total_[kW]"], color="black", linestyle=":", linewidth=1.5, label="Total")
    
    _apply_axis_styling(
        ax1, 
        title=f"{profile_key} - Profile & Excess", 
        ylabel="[kW]", 
        ylim=(0, max(df["Total_[kW]"].max() * 1.1, 7000))
    )
    ax1.legend(loc="upper left")
    
    # ---- BOTTOM PLOT: Isolated Excess/V2G ----
    if metrics_df.empty:
        ax2.plot(excess_df.index, [0] * len(excess_df), color="#b0bec5", linewidth=1)
        ax2.text(0.5, 0.5, "No Peaks Detected", ha='center', va='center', color='red', transform=ax2.transAxes)
        _apply_axis_styling(
            ax2, 
            ylabel="V2G Percentage [%]",
            xlabel="Time [h]", 
            ylim=(0, 100)
        )
    else:
        ax2.plot(excess_df.index, excess_df["V2G_Percentage"], color="#b0bec5", linewidth=1, alpha=0.5)
        
        unique_peaks = [p for p in metrics_df["Peak_ID"].unique() if p > 0]
        cmap = plt.colormaps["tab10"].resampled(max(len(unique_peaks), 1))
        
        for i, peak_id in enumerate(unique_peaks):
            peak_data = excess_df[excess_df["Peak_ID"] == peak_id]
            ax2.fill_between(
                peak_data.index, 0, peak_data["V2G_Percentage"], 
                color=cmap(i), alpha=0.6, label=f"Peak {int(peak_id)}"
            )
            
        v2g_max = excess_df["V2G_Percentage"].max()
        for _, row in metrics_df.iterrows():
            _add_peak_label(ax2, row, excess_df, v2g_max)
            
        _apply_axis_styling(
            ax2, 
            ylabel="V2G Percentage [%]", 
            xlabel="Time [h]", 
            ylim=(0, max(v2g_max * 1.1, 100))
        )
        ax2.legend(loc="upper left", framealpha=0.9)

    # Format shared X-axis ticks
    ax2.set_xticks(tick_intervals)
    ax2.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=9)
    
    # ---- BOTTOM METRICS GRID ----
    _add_metrics_table(fig, metrics_df)
    
    plt.close(fig)
    return fig


def _apply_axis_styling(ax, title=None, ylabel=None, xlabel=None, ylim=None):
    """Helper utility to keep plot aesthetic adjustments consistent."""
    if title: 
        ax.set_title(title, fontsize=14, fontweight="bold")
    if ylabel: 
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
    if xlabel: 
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    if ylim: 
        ax.set_ylim(ylim)
    ax.grid(True, linestyle="--", alpha=0.4)


def _add_peak_label(ax, row, excess_df, v2g_max):
    """Calculates peak midpoint and places metadata text box."""
    p_id = int(row["Peak_ID"])
    start, stop, max_v2g = row["Start_Time"], row["Stop_Time"], row["Max_V2G_[%]"]
    
    try:
        start_idx = excess_df.index.get_loc(start)
        stop_idx = excess_df.index.get_loc(stop)
        time_midpoint = excess_df.index[(start_idx + stop_idx) // 2]
    except (KeyError, ValueError):
        time_midpoint = start

    y_pos = max_v2g + (max(v2g_max, 10) * 0.03)
    
    ax.text(
        x=time_midpoint, y=y_pos, s=f"#{p_id}",
        color="black", fontsize=10, fontweight="bold", ha="center", va="bottom",
        bbox=dict(facecolor='white', edgecolor='#cfd8dc', boxstyle='round,pad=0.2', alpha=0.8)
    )


def _add_metrics_table(fig, metrics_df):
    """Generates a peak metrics table on a dedicated axis."""
    if metrics_df.empty:
        return
        
    # Filter out only the columns present in the COLUMN_RENAMING mapping
    keep_cols = [col for col in GRID_LABLE_MAPPING.keys() if col in metrics_df.columns]
    table_df = metrics_df[keep_cols].copy()
    
    # Clean up types and format data fields
    if "Peak_ID" in table_df.columns:
        table_df["Peak_ID"] = table_df["Peak_ID"].astype(int)
        
    if "Car_Count" in table_df.columns:
        table_df["Car_Count"] = table_df["Car_Count"].astype(int)
    
    for col in table_df.columns:
        if table_df[col].dtype in ['float64', 'float32']:
            table_df[col] = table_df[col].round(2)
            
    # Rename using your custom headers
    table_df = table_df.rename(columns = GRID_LABLE_MAPPING)
    
    headers = table_df.columns.tolist()
    cell_text = table_df.values.astype(str).tolist()
    
    # Add a slightly wider invisible axis to accommodate longer text strings
    table_ax = fig.add_axes([0.08, 0.04, 0.84, 0.12]) 
    table_ax.axis('off')
    
    # Create table
    metrics_table = table_ax.table(
        cellText=cell_text,
        colLabels=headers,
        cellLoc='center',
        loc='center'
    )
    
    metrics_table.auto_set_font_size(False)
    metrics_table.set_fontsize(9.5)
    metrics_table.scale(1, 1.3)
    
    # Set width based on column headers
    metrics_table.auto_set_column_width(col = list(range(len(headers))))
    
    # Apply styling
    for (row, col), cell in metrics_table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('black')
        else:
            cell.set_facecolor('white')