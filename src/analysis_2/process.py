#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 21:18:21 2022

@author: bomeyering
"""

########################
# file processing module#
########################

import pandas as pd
import datetime as dt
# import numpy as np
# import pandas as pd
import datetime


# import os
# import sys

def extract_angle(filename):
    """
	When passed a single argument, filename,
	Returns a data frame of the time stamp and the Y angle
	"""
    col_names = ['date_time', 'accel', 'a_x', 'a_y', 'a_z', 'velocity', 'v_x', 'v_y', 'v_z', 'angle', 'ang_x', 'ang_y',
                 'ang_z']
    raw = pd.read_table(filepath_or_buffer=filename,
                        sep=",",
                        header=None,
                        names=col_names,
                        usecols=col_names,
                        infer_datetime_format=True)

    raw[['date', 'timestamp']] = raw['date_time'].str.split(' ', expand=True)
    del raw['date_time']
    raw = raw.reindex(columns=['date', 'timestamp'] + col_names[2:])

    return raw


def extract_force(filename):
    """
	When passed a filename of a .csv force file
	Returns a data frame of the force in Newtons
	and a formatted timestamp
	"""

    col_names = ['index', 'force_n', 'units', 'seconds', 'time_units']
    raw = pd.read_csv(filepath_or_buffer=filename,
                      header=None,
                      skiprows=6,
                      index_col=False,
                      names=col_names,
                      usecols=['index', 'force_n', 'seconds'])

    return raw


def convert_secs(sec):
    """
	convert a float value of seconds to %H:%M:%S.%f format
	"""

    total_ms = sec * 1000
    ms = int(total_ms % 1000) * 1000
    s = int(total_ms) // 1000
    m = 0
    h = 0

    if s > 60:
        m += s // 60
        s = s % 60

    if m > 60:
        h += m // 60
        m = m % 60

    tf = dt.datetime(2021, 11, 4, h, m, s, ms)
    # 	formatted = dt.datetime.strftime(tf, format = '%Y-%M-%D %H:%M:%S.%f')
    # split = formatted.split()[1]

    return tf


def convert_secs2(sec):
    """
    convert a float value of seconds to datetime.datetime object
    Accurate represention of sub 24hr durations in seconds
    """
    import datetime

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

    today = datetime.date.today()  # get current date
    date_list = [today.year, today.month, today.day, h, m, s, us]  # list containing date elements
    dt = datetime.datetime(*date_list)

    return dt


def convert_timestamp(timestamp):
    '''
    Pass a timestamp in %h:%m:%s.%f format and convert it to an appropriate datetime object
    '''
    import re
    import datetime

    time_split = [int(i) for i in re.split(r'\W', timestamp)]
    today = datetime.date.today()  # get current date
    date_list = [today.year, today.month, today.day]  # current date used only for constructing datetime object

    return datetime.datetime(*(date_list + time_split))


def extract_angle_cleaned(filename, timestamp):
    '''
    Pass a filename and a video timestamp for the relative start time to normalize by
    return a data frame with the adjusted timestamp
    '''

    from os.path import exists
    import pandas as pd
    import datetime
    # import re

    assert type(filename) is str, f"{filename} is not formatted as a string"
    file_ex = exists(filename)
    assert file_ex == True, f"{filename} does not exist in this directory"
    assert type(timestamp) is datetime.datetime, f"{timestamp} is not a datetime.datetime object"

    # Read in the the IMU .txt file
    col_names = ['date_time', 'accel', 'a_x', 'a_y', 'a_z', 'velocity',
                 'v_x', 'v_y', 'v_z', 'angle', 'ang_x', 'ang_y', 'ang_z']
    raw_df = pd.read_table(filepath_or_buffer=filename,
                           sep=",",
                           header=None,
                           names=col_names,
                           usecols=col_names,
                           infer_datetime_format=True)

    raw_df['date_time'] = pd.to_datetime(raw_df.date_time)
    raw_df['date_time'] = raw_df.date_time - raw_df.date_time.min() + timestamp

    return raw_df


def resample_time(data, interval='.033333S', on='date_time'):
    '''
    Takes a data frame object with a date_time Series and resamples/interpolates according to a specified interval
    '''

    import pandas as pd

    assert type(data) is pd.core.frame.DataFrame
    assert type(interval) is str
    assert on in data.columns

    resample = data.resample(interval, on='date_time', origin='start').mean()
    intp = resample.interpolate(method='linear', limit_direction='forward')

    intp.reset_index(inplace=True)

    return intp


def extract_force_profile(filename):
    """
    When passed a filename of a .csv force file
    Returns a data frame of the force in Newtons
    """

    col_names = ['index', 'force_n', 'units', 'seconds', 'time_units']
    force = pd.read_csv(filepath_or_buffer=filename,
                        header=None,
                        skiprows=6,
                        index_col=False,
                        names=col_names,
                        usecols=['index', 'force_n', 'seconds'])

    return force


def normalize_force_time(data, timestamp):
    '''
    When passed an appropriate data frame and timestamp, normalizes the force timestamps to that of the video
    '''

    import re
    import pandas as pd
    import numpy as np
    import datetime
    assert type(data) == pd.core.frame.DataFrame
    assert type(timestamp) == datetime.datetime

    raw = data.copy()
    raw.seconds = raw.seconds.apply(convert_secs)
    min_t = raw.seconds.min()

    raw.seconds = raw.seconds + datetime.timedelta(hours=timestamp.hour,
                                                   minutes=timestamp.minute,
                                                   seconds=timestamp.second,
                                                   microseconds=timestamp.microsecond)

    raw = raw.rename(columns={'seconds': 'timestamp'})
    return raw


def common_set(dir1, dir2):
    '''
    gets the intersection of sets of filenames in two directories
    '''

    import os
    from re import sub
    list1 = [sub('\.\w*', '', s) for s in os.listdir(dir1)]
    list2 = [sub('\.\w*', '', s) for s in os.listdir(dir2)]

    return {i for i in set(list1).intersection(set(list2))}


def generate_merges(sample_id, timestamp_df):
    '''
    Takes an id as the argument, returns a 'nearest' merged dataframe containing the force and imu data for each time
    '''

    f_start = convert_timestamp(timestamp_df[timestamp_df.video_id == sample_id].values.item(1))
    imu_start = convert_timestamp(timestamp_df[timestamp_df.video_id == sample_id].values.item(2))

    clean_angle = extract_angle_cleaned(filename=''.join(['../imu_data/', sample_id, '.txt']), timestamp=imu_start)
    imu_resample = resample_time(clean_angle)

    clean_force = extract_force_profile(filename=''.join(['../force_gauge_data/', sample_id, '.csv']))
    force_norm = normalize_force_time(clean_force, f_start)

    merged = pd.merge_asof(force_norm, imu_resample, left_on='timestamp', right_on='date_time', direction='nearest')
    del merged['date_time']

    return merged


def generate_srt(df, sample_id=None):
    '''
    Generate an .srt subtitle file for each video
    '''
    import pandas as pd

    df1 = df.copy()
    pushed = df1.timestamp  # copy timestamp
    pushed.index = pushed.index - 1  # roll back the index value
    df2 = pd.merge(pushed, df1, left_index=True, right_index=True,
                   how='outer')  # merge on the index(lags the timestamp by one t)
    df2 = df2.rename(columns={'timestamp_x': 't_end', 'timestamp_y': 't_start'})
    df2.drop([-1], inplace=True)  # Drop ends
    df2.drop([df2.shape[0] - 1], inplace=True)

    df2[['NONE', 't_start']] = df2['t_start'].astype('str').str.split(expand=True)
    df2[['NONE', 't_end']] = df2['t_end'].astype('str').str.split(expand=True)
    del df2['NONE']
    df2['t_start'] = df2['t_start'].str[0:12]  # clip trailing zeros
    df2['t_end'] = df2['t_end'].str[0:12]

    df2['time_slice'] = df2.t_start + " --> " + df2.t_end  # create an srt timestamp string
    df2['time_slice'] = df2['time_slice'].str.replace('.', ',', regex=False)

    df2 = df2[['time_slice', 'force_n', 'a_x', 'a_y', 'a_z', 'v_x', 'v_y', 'v_z', 'ang_x', 'ang_y', 'ang_z']]

    with open(''.join(['./subtitles/', sample_id, '.srt']), 'w') as f:
        for ind, row in enumerate(df2.itertuples()):
            tmp_list = [str(ind), '\n', str(row[1]), '\n', '{\\an7}\n', f"ANGLE: {round(row[10], 1)}", '\n',
                        f'FORCE: {int(row[2])}', '\n\n']
            f.writelines(tmp_list)
    f.close()

    return ' '.join([sample_id, 'finished'])
