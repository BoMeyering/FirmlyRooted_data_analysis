"""
Excavation force profile alignment and calculation script
"""

import os
import pandas as pd
import numpy as np
from glob import glob

from src_py.file_utils import MergedDF, convert_secs, convert_timestamp, extract_angle_normalized, extract_force_normalized
from process_trunk_measurements import process_trunk_adair, process_pixel_depths

if __name__ == '__main__':

    #### PROP_ADAIR (FT2) ####

    # Trunk height measurements
    adair_trunk_path = './data/raw/excavation_data/trunk_height_measurements/prop_adair_trunk_heights.csv'

    # Preprocess the trunk height data
    processed_adair = process_trunk_adair(adair_trunk_path)

    # Output the preprocessed data
    processed_adair.to_csv('./data/processed/excavation_data/trunk_height_measurements/prop_adair_trunk_heights_processed.csv')

    # Get root system depths
    sys_depths = pd.read_csv('./data/raw/whole_root_system_measurements/prop_adair_root_system_measurement.csv')

    # Get pixel/cm scale and convert each sys_id depths to centimeters
    pixel_depths_path = './data/images/prop_adair_integral_pixel_depths.csv'
    vert_scale = pd.read_csv('./data/images/scale_images/vertical/vertical_scale_values_30cm.csv')
    scale_mean_px = vert_scale['eq_length_pixels'].mean()
    root_sys_depths = process_pixel_depths(pixel_depths_path, scale_pixels=scale_mean_px, scale_cm=30)

    # merge results
    sys_measure = pd.merge(left = sys_depths, right=processed_adair, on='sys_id')\
        .merge(root_sys_depths, on='sys_id')

    # set effort distance (h_e) from winch attachment to bottom of root system (pivot)
    sys_measure['h_e'] = sys_measure['crown_depth_cm'] + sys_measure['trunk_height_cm']

    # set resistance distance (h_r) from bottom of root system to root system center of pixel mass where the resistance is acting
    sys_measure['h_r'] = sys_measure['crown_depth_cm'] - sys_measure['load_depth_cm']

    # Output the full system measurment file
    sys_measure.to_csv('./data/processed/cleaned_data/prop_adair_system_depths.csv')
    print(sys_measure)

    # Grab imu and force file paths
    imu_dir = './data/raw/excavation_data/imu_sensor_data/prop_adair'
    force_dir = './data/raw/excavation_data/force_gauge_data/prop_adair'
    imu_files = glob("*.txt", root_dir=imu_dir)
    force_files = glob("*.csv", root_dir=force_dir)

    # Get common set of files and their timestamps
    intersection_files = set([i[:-4] for i in imu_files]).intersection(set([i[:-4] for i in force_files]))
    timestamps = pd.read_csv('./data/raw/excavation_data/video_time_stamps.csv', sep='\t')
    timestamps = timestamps.loc[timestamps.video_id.isin(list(intersection_files))]

    # Calculate excavation force for each root system
    for i in intersection_files:
        print(i)

        # Get the specific IMU and force profile paths
        imu_path = os.path.join(imu_dir, i+'.txt')
        force_path = os.path.join(force_dir, i+'.csv')
        # Extrac the start times for the IMU and force profiling
        imu_start = timestamps.loc[timestamps.video_id==i]['imu_start'].values[0]
        f_start = timestamps.loc[timestamps.video_id==i]['f_start'].values[0]

        # Initialize the merge dataframe and resample
        merge_df = MergedDF(
            angle_path=imu_path,
            force_path=force_path,
            imu_start=imu_start,
            f_start=f_start
        )
        merge_df.resample_and_merge()

        # Extract the merged results
        results = merge_df.merged_data

        # Grab the distance measurements for a specific root system
        measurements = sys_measure.loc[sys_measure['sys_id']==i.upper()]
        h_e = measurements['h_e'].values[0]
        h_r = measurements['h_r'].values[0]
        crown_depth = measurements['crown_depth_cm'].values[0]

        results['ang_rad'] = results['ang_y']*np.pi/180
        results['torque'] = results['force_n'] * h_e * np.sin(results['ang_rad'])

        ### DEPRECATED ###
        # calculate perpendicular and axial effort force components 
        results['winch_force_comp_perp_n'] = np.sin(results['ang_rad']) * results['force_n']
        results['winch_force_comp_axial_n'] = np.cos(results['ang_rad']) * results['force_n']
        ### DEPRECATED ###

        # calculate force at root load point DEPRECATED
        # results['root_load_force_n'] = results['winch_force_comp_perp_n']*h_e/h_r
        results['root_resistance_force_n'] = results['force_n'] * h_e / h_r
        

        # calculate effort at 30cm above soil level
        std_h_e = crown_depth + 30
        results['std_trunk_effort_n'] = results['force_n'] * h_e / std_h_e
        results['std_trunk_moment'] = results['std_trunk_effort_n'] * std_h_e * np.sin(results['ang_rad']) / 100  # Torque (turning moment) measured in Newton meters (N * m)

        results['he'] = h_e
        results['std_he'] = std_h_e
        

        out_path = os.path.join('./data/processed/excavation_data/processed_force_profiles/prop_adair', i+'.csv')
        results.to_csv(out_path)
