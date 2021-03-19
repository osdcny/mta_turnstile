"""
Load weekly turnstile data files into one single dataframe
"""

import os
import pandas as pd


def load_turnstile_data(file_directory=os.path.join('data', 'raw'),
                        first_file='turnstile_190105.txt'):
    """
    Load weekly turnstile data files into one single dataframe
    ----------
    file_directory: the location where raw weekly files are saved.
    first_file: first file to use. It depends on the starting period of analysis.

    Returns
    -------
    a single pandas dataframe
    """

    # Generate a list of files in the file directory
    all_files = os.listdir(file_directory)
    all_files.sort()

    # Generate a list of files to load (with directory name)
    file_index = all_files.index(first_file)
    _file_list = [os.path.join(file_directory, file) for file in all_files[file_index:]]

    # Read all the files and concat them into a single dataframe
    _df = pd.concat([pd.read_csv(file) for file in _file_list])
    _df.rename(columns=lambda x: x.strip(), inplace=True)  # Basic Cleaning

    return _df


if __name__ == '__main__':
    df = load_turnstile_data(file_directory=os.path.join('..', 'data', 'raw'), first_file='turnstile_190105.txt')
    print(df.head())
