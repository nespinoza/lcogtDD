# -*- coding: utf-8 -*-
import os
import time
import sys
import argparse
import calendar
import requests
import numpy as np


def parse_args():
    """Parse command-line inputs"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-sdate', default=None,
                        help='Start date for search [YYYY-MM-DD]')
    parser.add_argument('-edate', default=None,
                        help='End date for search. [YYYY-MM-DD]')
    parser.add_argument('-proposalID', default=None,
                        help='List of proposals to search for')
    parser.add_argument('-datafolder', default=None,
                        help='Directory where the data will be downloaded into.')
    parser.add_argument('-flatdir', action='store_true',
                        help='Use a flat directory structure instead of sorting into date subdirectories')
    parser.add_argument('-spectra', action='store_true',
                        help='Only download NRES spectral packages (ending w/ .tar.gz)')

    args = parser.parse_args()

    return args


def download_frames(sdate, edate, headers, prop, datafolder):
    """Download files

      This function downloads all the frames for a given range of dates, querying
      50 frames at a time (i.e., if 150 frames have to be downloaded, the process 
      is repeated 3 times, each time downloading 50 frames). This number 
      assumes connections can be as bad as to be able to download only ~1 Mb per 
      minute (each get request shares file urls that last 48 hours only), assuming 
      60 MB frames (worst case scenarios).
 
      It returns the number of total identified frames for the given range and the 
      number of frames downloaded (which is equal to the number of identified frames 
      if no data for that time range was detected on the system).

      Args:
          sdate (time.time): Search for data collected on this date or later
          edate (time.time): Search for data collected before this date
          headers (dict): authentication token from the LCO archive
          prop (list): List of proposal IDs to search for
          datafolder (string): Directory to put the data

    """
    nidentified = 0
    ndownloaded = 0
    response = requests.get('https://archive-api.lco.global/frames/?' +
                            'limit=50&' +
                            'RLEVEL=91&' +
                            'start='+sdate+'&' +
                            'end='+edate+'&' +
                            'PROPID=' + prop,
                            headers=headers).json()

    frames = response['results']
    if len(frames) != 0:
        print('\t > Frames identified for the '+sdate+'/'+edate+' period. Checking frames...')
        while True:
            for frame in frames:
                nidentified += 1
                # Get date of current image frame:
                date = frame['filename'].split('-')[2]

                # Create new folder with the date if not already there:
                if args.flatdir:
                    outpath = datafolder
                else:
                    outpath = os.path.join(datafolder, 'raw', date)
                if not os.path.exists(outpath):
                    os.mkdir(outpath)

                # Check if file is already on disk and that is not a _cat.fits. If not there
                # and is not a _cat.fits, download the file:
                if not os.path.exists(os.path.join(outpath, frame['filename'])) and\
                   '_cat.fits' != frame['filename'][-9:]:
                    if args.spectra and not frame['filename'].endswith('.tar.gz'):
                        continue
                    print('\t   + File '+frame['filename']+' not found in '+outpath)
                    print('\t     Downloading ...')
                    with open(os.path.join(outpath, frame['filename']), 'wb') as f:
                        f.write(requests.get(frame['url']).content)
                    ndownloaded += 1
            if response.get('next'):
                response = requests.get(response['next'], headers=headers).json()
                frames = response['results']
            else:
                break
    return nidentified, ndownloaded


def get_headers_from_token(username, password):
    """
      This function gets an authentication token from the LCO archive.

      Args:
          username (string): User name for LCO archive
          password (string): Password for LCO archive
      Returns:
          dict: LCO authentication token
    """
    # Get LCOGT token:
    response = requests.post('https://archive-api.lco.global/api-token-auth/',
                             data={'username': username,
                                   'password': password}
                             ).json()

    token = response.get('token')

    # Store the Authorization header
    headers = {'Authorization': 'Token ' + token}
    return headers


if __name__ == '__main__':
    args = parse_args()

    starting_date = args.sdate
    ending_date = args.edate
    propID = args.proposalID
    dfolder = args.datafolder

    print('\n\t ----------------------------------------------')
    print('\t                lcogtDD v.1.2.\n')
    print('\t Author: Nestor Espinoza (nespino@astro.puc.cl)')
    print('\t                         (github@nespinoza)')
    print('\t w/ contributions from: BJ Fulton (bfulton@caltech.edu)')
    print('\t                                  (github@bjfultn)')
    print('\t ----------------------------------------------\n')
    # Check that user input is ok:
    if starting_date is None:
        print('\t lgogtDD input error: Please, insert a starting date from which')
        print('\t                      to download data from. Usage example:\n')
        print('\t                        python download_data -sdate 2016-04-01')
        print('\n')
        sys.exit()

    # Get current date (in order to explore it, we need to leave
    # ending_date = ending_date + 1 day:
    if ending_date is None:
        ending_date = time.strftime("%Y-%m-%d")
        print('\t > Checking data from {} to {}...\n'.format(starting_date, ending_date))
        c_y, c_m, c_d = ending_date.split('-')
        if int(c_d) + 1 <= calendar.monthrange(int(c_y), int(c_m))[-1]:
            ending_date = c_y + '-' + c_m + '-' + str(int(c_d) + 1)
        elif int(c_m) + 1 <= 12:
            ending_date = c_y + '-' + str(int(c_m) + 1) + '-01'
        else:
            ending_date = str(int(c_y) + 1) + '-01-01'
    else:
        print('\t > Checking data from {} to {}...\n'.format(starting_date, ending_date))
    # Get data from user file:
    f = open('userdata.dat', 'r')
    username = (f.readline().split('=')[-1]).split()[0]
    password = (f.readline().split('=')[-1]).split()[0]
    datafolder = (f.readline().split('=')[-1]).split()[0]
    proposals = (f.readline().split('=')[-1]).split(',')

    if propID is not None:
        proposals = propID.split(',')

    if dfolder is not None:
        datafolder = dfolder

    print('\t > Proposals from which data will be fetched: {}'.format(' '.join(proposals)))
    for i in range(len(proposals)):
        proposals[i] = proposals[i].split()[0]
    f.close()

    #  Create raw folder inside data folder if not existent:
    if not os.path.exists(datafolder + '/raw/'):
        os.mkdir(datafolder + '/raw/')

    headers = get_headers_from_token(username, password)

    # Get frame names from starting to ending date:
    for prop in proposals:
        prop_frame_names = np.array([])
        prop_frame_urls = np.array([])
        c_y, c_m, c_d = starting_date.split('-')
        e_y, e_m, e_d = np.array(ending_date.split('-')).astype('int')
        while True:
            sdate = c_y + '-' + c_m + '-' + c_d
            if int(c_d) + 1 <= calendar.monthrange(int(c_y), int(c_m))[-1]:
                edate = c_y + '-' + c_m + '-' + str(int(c_d) + 1)
            elif int(c_m) + 1 <= 12:
                edate = c_y + '-' + str(int(c_m) + 1) + '-01'
            else:
                edate = str(int(c_y) + 1) + '-01-01'

            # Download frames in the defined time ranges:
            nidentified, ndownloaded = download_frames(sdate, edate, headers, prop, datafolder)
            if nidentified != 0:
                print('\t   Final count: ' + str(nidentified) + ' identified frames, downloaded ' +
                      str(ndownloaded) + ' new ones.')

            # Get next year, month and day to look for. If it matches the user-defined
            # or current date, then we are done:
            c_y, c_m, c_d = edate.split('-')
            if int(c_y) == e_y and int(c_m) == e_m and int(c_d) == e_d:
                break

    print('\n\t Done!\n')
