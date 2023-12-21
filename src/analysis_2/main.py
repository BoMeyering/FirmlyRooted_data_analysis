import os
import pandas as pd
import numpy as np
from glob import glob

from file_utils import MergedDF, convert_secs, convert_timestamp, extract_angle_normalized, extract_force_normalized
from process_trunk_measurements import process_trunk_adair, process_pixel_depths

if __name__ == '__main__':

    #### PROP_ADAIR ####
    # trunk height measurements
    adair_trunk_path = './data/raw/excavation_data/trunk_height_measurements/prop_adair_trunk_heights.csv'

    processed_adair = process_trunk_adair(adair_trunk_path)

    processed_adair.to_csv('./data/processed/excavation_data/trunk_height_measurements/prop_adair_trunk_heights_processed.csv')

    # get root system depths
    sys_depths = pd.read_csv('./data/raw/whole_root_system_measurements/prop_adair_root_system_measurement.csv')

    # get pixel depths for sys_id
    pixel_depths_path = './data/images/prop_adair_integral_pixel_depths.csv'
    vert_scale = pd.read_csv('./data/images/scale_images/vertical/vertical_scale_values_30cm.csv')
    scale_mean_px = vert_scale['eq_length_pixels'].mean()
    root_sys_depths = process_pixel_depths(pixel_depths_path, scale_pixels=scale_mean_px, scale_cm=30)

    # merge results
    sys_measure = pd.merge(left = sys_depths, right=processed_adair, on='sys_id')\
        .merge(root_sys_depths, on='sys_id')

    # set effort distance from winch attachment to bottom of root system
    sys_measure['e_dist'] = sys_measure['crown_depth_cm'] + sys_measure['trunk_height_cm']

    # sef load distance from bottom of root system to root system center of pixel mass
    sys_measure['l_dist'] = sys_measure['crown_depth_cm'] - sys_measure['load_depth_cm']

    print(sys_measure)

    imu_dir = './data/raw/excavation_data/imu_sensor_data/prop_adair'
    force_dir = './data/raw/excavation_data/force_gauge_data/prop_adair'
    imu_files = glob("*.txt", root_dir=imu_dir)
    force_files = glob("*.csv", root_dir=force_dir)

    intersection_files = set([i[:-4] for i in imu_files]).intersection(set([i[:-4] for i in force_files]))
    timestamps = pd.read_csv('./data/raw/excavation_data/video_time_stamps.csv', sep='\t')
    timestamps = timestamps.loc[timestamps.video_id.isin(list(intersection_files))]

    for i in intersection_files:
        print(i)
        imu_path = os.path.join(imu_dir, i+'.txt')
        force_path = os.path.join(force_dir, i+'.csv')
        imu_start = timestamps.loc[timestamps.video_id==i]['imu_start'].values[0]
        f_start = timestamps.loc[timestamps.video_id==i]['f_start'].values[0]
        merge_df = MergedDF(
            angle_path=imu_path,
            force_path=force_path,
            imu_start=imu_start,
            f_start=f_start
        )
        merge_df.resample_and_merge()

        results = merge_df.merged_data
        # print(results)
        
        measurements = sys_measure.loc[sys_measure['sys_id']==i.upper()]
        e_dist = measurements['e_dist'].values[0]
        l_dist = measurements['l_dist'].values[0]
        crown_depth = measurements['crown_depth_cm'].values[0]

        results['ang_rad'] = results['ang_y']*np.pi/180
        results['torque'] = results['force_n'] * e_dist * np.sin(results['ang_rad'])

        # calculate perpendicular and axial effort force components
        results['winch_force_comp_perp_n'] = np.sin(results['ang_rad']) * results['force_n']
        results['winch_force_comp_axial_n'] = np.cos(results['ang_rad']) * results['force_n']

        # calculate force at root load point
        results['root_load_force_n'] = results['winch_force_comp_perp_n']*e_dist/l_dist

        # calculate effort at 3 feet above soil level
        std_e_dist = crown_depth + 91.44
        results['std_trunk_effort_n'] = results['winch_force_comp_perp_n'] * e_dist / std_e_dist
        print(results)

        out_path = os.path.join('./data/processed/excavation_data/processed_force_profiles/prop_adair', i+'.csv')
        results.to_csv(out_path)
