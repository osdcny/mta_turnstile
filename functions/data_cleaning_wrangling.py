"""
Cleaning and transforming the single pandas dataframe
"""

import os

import numpy as np
import pandas as pd
from scipy import stats


def clean_and_wrangle(_df, station_info_path=os.path.join('references', 'nyc_subway_station_info.csv')):
    # Create datetime columns
    _df['DATETIME'] = pd.to_datetime(_df['DATE'] + ' ' + _df['TIME'])  # Create Datetime variable
    _df['DATE'] = pd.to_datetime(_df['DATE'], infer_datetime_format=True)  # Convert Date Variable to datetime format
    # _df['PERIOD'] = _df['DATE'].dt.to_period('M') #Show YEAR-MONTH
    _df['PERIOD'] = _df['DATE'].values.astype('datetime64[M]')  # Show YEAR-MONTH-DAY (DAY is 01)

    # Create Unique Station Names
    # 'LINENAME' is added because multiple stations could have the same name.
    _df['STATION_NAME_RAW'] = _df['STATION'] + "-" + _df['LINENAME']

    # Create Unique ID for turnstiles
    # 'UNIT' is for 'remote unit'. Generally, each station is a remote unit.
    # Larger stations sometimes have several remote units.
    # 'C/A' is for control area.
    # Each control area is  a group of turnstiles that are physically located in the same exit.
    # 'C/A' is unique within a control area.
    # SCP “subunit channel position”. It is the ID number of a single turnstile.
    # SCP is unique within a control area.
    _df['TURNSTILE'] = _df['UNIT'] + "-" + _df['C/A'] + "-" + _df['SCP']
    # Filter: only these three divisions
    # These three divisions represent the entire NYC Subway system.
    _df = _df[_df['DIVISION'].isin(["BMT", "IND", "IRT"])]
    # Filter Based on Time
    # This is to filter our random data records.
    _df = _df[(_df.TIME.str[-5:] == '00:00') | (_df.TIME.str[-5:] == '30:00')]
    # Remove ORCHARD Beach 6 station
    # (This station is not available anywhere in the MTA System)
    _df = _df[_df['STATION_NAME_RAW'] != 'ORCHARD BEACH-6']

    # Only turnstiles more than a threshold is included
    turnstile_counts = _df.groupby('TURNSTILE').size()
    # turnstile_threshold = np.quantile(turnstile_counts, .02)
    turnstile_threshold = stats.mode(turnstile_counts)[0][0] * 0.1
    turnstile_list = list(turnstile_counts[turnstile_counts > turnstile_threshold].index)
    # DF only includes turnstiles on the list
    _df = _df[_df.TURNSTILE.isin(turnstile_list)]
    _df = _df.sort_values(by=['TURNSTILE', 'DATETIME'])

    # Calculate the differences
    _df['ENTRIES_DIFF'] = _df['ENTRIES'].diff()
    _df['EXITS_DIFF'] = _df['EXITS'].diff()

    # Filter: records more than 7200 are counted as 0, since it is very likely a wrong number.
    # Transformation: take the absolute value, since some numbers are negative
    # 4 hours * 60 minutes * 60 seconds / 2
    usage_threshold_4hours = 7200  # 2 seconds per swipe
    _df['ENTRIES_DIFF'] = np.where(abs(_df['ENTRIES_DIFF']) < usage_threshold_4hours, abs(_df['ENTRIES_DIFF']), 0)
    _df['EXITS_DIFF'] = np.where(abs(_df['EXITS_DIFF']) < usage_threshold_4hours, abs(_df['EXITS_DIFF']), 0)

    station_info = pd.read_csv(station_info_path, sep=',', encoding='cp1252',
                               usecols=['STATION_NAME_RAW', 'STATION_NAME', 'Latitude',
                                        'Longitude', 'Neighborhood', 'PUMA', 'Borough'])

    _df = pd.merge(_df, station_info, on='STATION_NAME_RAW', how='left')

    _df = _df[['DATE', 'PERIOD', 'ENTRIES_DIFF', 'EXITS_DIFF', 'TURNSTILE', 'STATION_NAME', 'Neighborhood', 'PUMA',
               'Borough']]

    # Change one column name
    _df.rename(columns={'STATION_NAME': 'STATION'}, inplace=True)
    # Change all column names to lower case
    _df.rename(str.lower, axis='columns', inplace=True)

    return _df
