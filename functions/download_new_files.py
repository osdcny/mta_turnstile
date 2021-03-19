"""
Function that checks for new files from the MTA website.
If new files exist, they are downloaded to the data/rawf folder.
"""

import os

import requests
from bs4 import BeautifulSoup


def download_new_files(file_directory=os.path.join('data', 'raw')):
    # Check all the turnstile files that are available to be download on the mta website.
    file_url = 'http://web.mta.info/developers/turnstile.html'
    page = requests.post(file_url)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding=page.encoding.lower())

    all_links = soup.find_all('a', href=True)
    available_files = [link['href'].split('data/nyct/turnstile/')[1] for link in all_links if
                       'data/nyct/turnstile/' in link['href']]

    # Check existing files in the data/raw folder
    all_files = os.listdir(file_directory)
    existing_files = [file for file in all_files]

    # Generate a list of files that needs to be downloaded
    download_list = list(set(available_files) - set(existing_files))

    if len(download_list) == 0:
        print('No new files need to be downloaded.')
    else:
        print(f'{len(download_list)} new file(s) will be downloaded to the data folder.')

    # Download the new files
    for file in download_list:
        base_url = 'http://web.mta.info/developers/data/nyct/turnstile/'
        file_url = f'{base_url}{file}'
        file_dl = requests.get(file_url)
        # file_name = url.rsplit('/', 1)[-1]
        file_path = os.path.join(file_directory, file)
        open(file_path, 'wb').write(file_dl.content)


if __name__ == '__main__':
    download_new_files(file_directory=os.path.join('..', 'data', 'raw'))
