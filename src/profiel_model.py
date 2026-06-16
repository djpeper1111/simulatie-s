# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 10:14:35 2026

@author: Luuk
"""

import pandas as pd

COLUMN_MAPPING = {
    "homeappliances": "Homeappliances_[kW]",
    "utilities": "Utilities_[kW]",
    "heating": "Heating_[kW]",
    "water": "Water_[kW]",
    "vehicles": "Vehicles_[kW]"
}

def scale_vehicle_series(
        df, 
        vehicle_count, 
        base_count = 167
    ):
    
    df_copy = df.copy()
    
    if "vehicles" in df_copy.columns:
        factor = vehicle_count / base_count
        df_copy["vehicles"] = df_copy["vehicles"] * factor
    
    return df_copy


def analyze_excess(
        excess_df, 
        vehicle_count, 
        car_capacity_kWh,
        V2G_power_kW
    ):
    # Init columns
    excess_df[["Peak_ID", "V2G_Count", "V2G_Percentage", "Total_[kWh]"]] = 0.0

    # Identify where peaks occur
    peak_mask = excess_df["Excess_[kW]"] > 0
    if not peak_mask.any():
        return excess_df, pd.DataFrame()
    
    # Calculations for rows with excess
    excess_df.loc[peak_mask, "V2G_Count"] = (excess_df.loc[peak_mask, "Excess_[kW]"] / V2G_power_kW).round()
    excess_df.loc[peak_mask, "V2G_Percentage"] = (excess_df.loc[peak_mask, "V2G_Count"] / vehicle_count) * 100
    excess_df.loc[peak_mask, "Total_[kWh]"] = excess_df.loc[peak_mask, "Excess_[kW]"] * 0.25
    
    # Define peak groups based on a 2-hour gap threshold
    peaks_df = excess_df[peak_mask]
    time_diffs = pd.to_timedelta(peaks_df.index).diff()
    peak_groups = (time_diffs > pd.Timedelta(hours = 2)).cumsum() + 1
    
    # Map group IDs back to the excess dataframe
    excess_df.loc[peak_mask, "Peak_ID"] = peak_groups.astype(float)
    
    # Generate aggregate peak metrics using groupby
    peak_metrics = []
    for peak_id, group_df in excess_df[peak_mask].groupby("Peak_ID"):
        total_kwh = group_df["Total_[kWh]"].sum()
        max_cars = group_df["V2G_Count"].max()
        
        min_avg_battery = ((total_kwh / max_cars) / car_capacity_kWh) * 100 if max_cars > 0 else 0.0
        
        peak_metrics.append({
            "Peak_ID": int(peak_id),
            "Start_Time": group_df.index[0],
            "Stop_Time": group_df.index[-1],
            "Car_Count": max_cars,
            "Max_V2G_[%]": group_df["V2G_Percentage"].max(),
            "Total_[kWh]": total_kwh,
            "Min_Average_Battery_[%]": min_avg_battery
        })
    
    return excess_df, pd.DataFrame(peak_metrics)


def process_profiles(
        profiles_folder,
        vehicle_count = 167,
        car_capacity_kWh = 40,
        V2G_power_kW = 11,
        limit_kW = 5000
    ):
    profile_df_dict = {}
    columns_to_sum = list(COLUMN_MAPPING.values())
    
    for file_path in profiles_folder.glob("*.csv"):
        clean_key = file_path.stem.split(" - ")[-1]
        
        # Pipeline transformations for clean data
        df = (
            pd.read_csv(file_path)
            .set_index("time")
            .pipe(scale_vehicle_series, vehicle_count)
            .rename(columns=COLUMN_MAPPING)
        )
        df.index.name = "Time_[h]"
        
        # Add and calculate columns
        df["Total_[kW]"] = df[columns_to_sum].sum(axis=1)
        df["Limit_[kW]"] = limit_kW
        
        # Generation of the excess dataframe
        excess_df = pd.DataFrame(index=df.index)
        excess_df["Excess_[kW]"] = (df["Total_[kW]"] - limit_kW).clip(lower=0)
        
        excess_df, metrics_df = analyze_excess(
            excess_df=excess_df,
            vehicle_count=vehicle_count,
            car_capacity_kWh=car_capacity_kWh,
            V2G_power_kW=V2G_power_kW
        )
        
        profile_df_dict[clean_key] = {
            "profile": df,
            "excess": excess_df,
            "metrics": metrics_df
        }
        
    return profile_df_dict