# -*- coding: utf-8 -*-
import os
import time
import sys
import argparse
import calendar
import requests
import numpy as np

# Get user input:
parser = argparse.ArgumentParser()
parser.add_argument('-sdate',default=None)
parser.add_argument('-edate',default=None)
args = parser.parse_args()

starting_date = args.sdate
ending_date = args.edate

print '\n\t ----------------------------------------------'
print '\t                lcogtDD v.1.0.\n'
print '\t Author: Nestor Espinoza (nespino@astro.puc.cl)'
print '\t                         (github@nespinoza)'
print '\t ----------------------------------------------\n'
# Check that user input is ok:
if starting_date is None:
    print '\t lgogtDD input error: Please, insert a starting date from which'
    print '\t                      to download data from. Usage example:\n'
    print '\t                        python download_data -sdate 2016-04-01'
    print '\n'
    sys.exit()

# Get current date (in order to explore it, we need to leave
# ending_date = ending_date + 1 day:
if ending_date is None:
    ending_date = time.strftime("%Y-%m-%d") 
    print '\t > Checking data from '+starting_date+' to '+ending_date+'...\n'
    c_y,c_m,c_d = ending_date.split('-')
    if int(c_d)+1 <= calendar.monthrange(int(c_y),int(c_m))[-1]:
        ending_date = c_y+'-'+c_m+'-'+str(int(c_d)+1)
    elif int(c_m)+1 <= 12:
        ending_date = c_y+'-'+str(int(c_m)+1)+'-01'
    else:
        ending_date = str(int(c_y)+1)+'-01-01'
else:
    print '\t > Checking data from '+starting_date+' to '+ending_date+'...\n'
# Get data from user file:
f = open('userdata.dat','r')
username = (f.readline().split('=')[-1]).split()[0]
password = (f.readline().split('=')[-1]).split()[0]
datafolder = (f.readline().split('=')[-1]).split()[0]
proposals = (f.readline().split('=')[-1]).split(',')

for i in range(len(proposals)):
    proposals[i] = proposals[i].split()[0]
f.close()

# Create raw folder inside data folder if not existent:
if not os.path.exists(datafolder+'/raw/'):
    os.mkdir(datafolder+'/raw/')

def get_all_framenames(sdate,edate,headers,prop):
    response = requests.get('https://archive-api.lcogt.net/frames/?'+\
                    'limit=1000&'+\
                    'RLEVEL=90&'+\
                    'start='+sdate+'&'+\
                    'end='+edate+'&'+\
                    'PROPID='+prop,\
                    headers=headers).json()

    frames = response['results']
    if len(frames) == 0:
        return np.array([]),np.array([])
    else:
        fnames = np.array([])
        furls = np.array([])
        for frame in frames:
            fnames = np.append(fnames,frame['filename'])
            furls = np.append(furls,frame['url'])
        return fnames,furls

def get_headers_from_token(username,password):
    # Get LCOGT token:
    response = requests.post(
       'https://archive-api.lcogt.net/api-token-auth/',
      data = {
          'username': username,
          'password': password
        }
    ).json()

    token = response.get('token')

    # Store the Authorization header
    headers = {'Authorization': 'Token ' + token}
    return headers

headers = get_headers_from_token(username,password)

# Get frame names from starting to ending date:
for prop in proposals:
    prop_frame_names = np.array([])
    prop_frame_urls = np.array([])
    c_y,c_m,c_d = starting_date.split('-')
    e_y,e_m,e_d = np.array(ending_date.split('-')).astype('int')
    while True:
        sdate = c_y+'-'+c_m+'-'+c_d
        if int(c_d)+1 <= calendar.monthrange(int(c_y),int(c_m))[-1]:
            edate = c_y+'-'+c_m+'-'+str(int(c_d)+1)
        elif int(c_m)+1 <= 12:
            edate = c_y+'-'+str(int(c_m)+1)+'-01'
        else:
            edate = str(int(c_y)+1)+'-01-01'
        frame_names, frame_urls = get_all_framenames(sdate,edate,headers,prop)
        if len(frame_names)>0:
            print '\t > '+str(len(frame_names))+' frames collected for proposal '+prop+' between '+sdate+' and '+edate+'...'
            print '\t > Downloading frames...'
            for i in range(len(frame_names)):
                framename = frame_names[i]
                frameurl = frame_urls[i]

                # Get date of current image frame:
                date = framename.split('-')[2]

                # Create new folder with the date if not already there:
                if not os.path.exists(datafolder+'/raw/'+date+'/'):
                    os.mkdir(datafolder+'/raw/'+date+'/')

                # Check if file is already on folder. If not, download the file:
                if not os.path.exists(datafolder+'/raw/'+date+'/'+framename):
                    print '\t   + File '+framename+' not found on '+datafolder+'/raw/'+date+'/.'
                    print '\t     Downloading ...'
                    content = requests.get(frameurl).content
                    if 'expired' in content.lower():
                        print '\t > Session expired. Logging in again...'
                        edate = sdate
                    else:
                        with open(datafolder+'/raw/'+date+'/'+framename,'wb') as f:
                            f.write(content)
        c_y,c_m,c_d = edate.split('-')
        if int(c_y) == e_y and int(c_m) == e_m and int(c_d) == e_d:
            break
        else:
            # Get new headers/tokens to bypass apparent download limit that corrupt files:
            headers = get_headers_from_token(username,password)

print '\n\t Done!\n'
