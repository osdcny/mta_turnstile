import os

import pandas as pd
import numpy as np

from functions.download_new_files import download_new_files
from functions.load_weekly_files import load_turnstile_data
from functions.data_cleaning_wrangling import clean_and_wrangle
from functions.summarize import generate_usage_stats, generate_nominal_stats

# from functions import download_new_files as dl

if __name__ == "__main__":

    # Check MTA website see if there are any new files
    download_new_files()

    # Load weekly files into a single dataframe
    df = load_turnstile_data(file_directory=os.path.join("data", "raw"),
                             first_file="turnstile_190105.txt")

    # Clean, filter and transform the dataset
    df = clean_and_wrangle(df, station_info_path=os.path.join('references', 'nyc_subway_station_info.csv'))

    summary = generate_usage_stats(_df=df, level='station', window=12, first_period='2020-04-01',
                                   last_period='2021-02-01', add_city_total=True, comparison_type='base_year')
    
    
    reports_dir = 'reports'
    file_name = f'station_summary_feb_2021.csv'
    file_path = os.path.join(reports_dir, file_name)

    # summary.to_csv(file_path, index=False)


    # nominal_usage = generate_nominal_stats(df, level='station', add_city_total=True)
    
    # reports_dir = 'reports'
    # file_name = f'station_nominal_stats_feb_2021.csv'
    # file_path = os.path.join(reports_dir, file_name)

    # nominal_usage.to_csv(file_path)
