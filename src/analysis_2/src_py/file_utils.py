"""
File extraction and merging utility classes and functions
"""

import numpy as np
import pandas as pd
from glob import glob
import os
import datetime as dt
import re

class MergedDF:
    """
    
    """
    def __init__(self, angle_path, force_path, imu_start, f_start) -> None:
        
        self.angle_path = angle_path
        self.force_path = force_path
        self.imu_start = convert_timestamp(imu_start)
        self.f_start = convert_timestamp(f_start)
        self.angle_df = extract_angle_normalized(angle_path, self.imu_start)
        self.force_df = extract_force_normalized(force_path, self.f_start)


    def resample_and_merge(self):
        """
        Resamples self.angle_df based on the frequency of the force file
        """

        angle_df = self.angle_df.copy().resample(
            rule='0.033333s',
            origin='start'
        ).mean()

        force_df = self.force_df.copy()

        angle_df = angle_df.interpolate(
            method='linear',
            limit_direction='forward'
        )

        merged = pd.merge_asof(force_df, angle_df, left_index=True, right_index=True, direction='nearest')
        merged['ang_y'] = merged['ang_y'].abs()
        self.merged_data = merged

        return self.merged_data

    
def convert_secs(sec):
    """
    convert a float value of seconds to datetime.datetime object
    Accurate represention of sub 24hr durations in seconds
    """

    assert type(sec) is float

    total_us = sec * 1000000  # total microseconds
    us = int(total_us % 1000000)  # integer microseconds
    s = int(total_us) // 1000000  # integer seconds
    m = 0  # initial value for minutes
    h = 0  # initial value for hours

    if s >= 60:
        m += s // 60
        s = s % 60

    if m >= 60:
        h += m // 60
        m = m % 60

    date_list = [2021, 11, 4, h, m, s, us]  # list containing date elements
    time = dt.datetime(*date_list)

    return time

def convert_timestamp(timestamp):
    '''
    Pass a timestamp in %h:%m:%s.%f format and convert it to an appropriate datetime object
    '''
    import re
    import datetime

    time_split = [int(i) for i in re.split(r'\W', timestamp)]
    # today = datetime.date.today()
    date_list = [2021, 11, 4]  # current date used only for constructing datetime object

    return datetime.datetime(*(date_list + time_split))

def extract_angle_normalized(filename: str, timestamp: dt.datetime):
    '''
    Pass a filename and a video timestamp for the relative start time to normalize by
    return a data frame with the adjusted timestamp
    '''

    assert type(filename) is str, f"{filename} is not formatted as a string"
    file_ex = os.path.exists(filename)
    assert file_ex == True, f"{filename} does not exist in this directory"
    assert type(timestamp) is dt.datetime, f"{timestamp} is not a datetime.datetime object"

    # Read in the the IMU .txt file
    col_names = ['date_time', 'accel', 'a_x', 'a_y', 'a_z', 'velocity',
                 'v_x', 'v_y', 'v_z', 'angle', 'ang_x', 'ang_y', 'ang_z']
    data = pd.read_table(filepath_or_buffer=filename,
                           sep=",",
                           header=None,
                           names=col_names,
                           usecols=col_names)

    data['date_time'] = pd.to_datetime(data.date_time)
    data['date_time'] = data.date_time - data.date_time.min() + timestamp

    data = data[['date_time', 'ang_y']].set_index('date_time')

    return data

def extract_force_normalized(filename: str, timestamp: dt.datetime):
    """
    When passed a filename of a .csv force file
    Returns a data frame of the force in Newtons
    """

    col_names = ['index', 'force_n', 'units', 'seconds', 'time_units']
    data = pd.read_csv(filepath_or_buffer=filename,
                        header=None,
                        skiprows=6,
                        index_col=False,
                        names=col_names,
                        usecols=['index', 'force_n', 'seconds'])
    
    data.seconds = data.seconds.apply(convert_secs)
    data.seconds = data.seconds + dt.timedelta(hours=timestamp.hour,
                                                   minutes=timestamp.minute,
                                                   seconds=timestamp.second,
                                                   microseconds=timestamp.microsecond
                                                   )
    
    data = data.rename(columns={'seconds': 'date_time'}).set_index('date_time')
    del data['index']

    return data


if __name__ == '__main__':

    imu_dir = './data/raw/excavation_data/imu_sensor_data/prop_adair'
    force_dir = './data/raw/excavation_data/force_gauge_data/prop_adair'
    imu_files = glob("*.txt", root_dir=imu_dir)
    force_files = glob("*.csv", root_dir=force_dir)

    intersection_files = set([i[:-4] for i in imu_files]).intersection(set([i[:-4] for i in force_files]))
    timestamps = pd.read_csv('./data/raw/excavation_data/video_time_stamps.csv', sep='\t')
    timestamps = timestamps.loc[timestamps.video_id.isin(list(intersection_files))]

    for i in intersection_files:
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

        print(results)
