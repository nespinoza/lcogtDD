# -*- coding: utf-8 -*-
import os
import time
import argparse
import calendar
import requests
import numpy as np

# Get user input:
parser = argparse.ArgumentParser()
parser.add_argument('-sdate',default='2016-04-01')
parser.add_argument('-edate',default=None)
args = parser.parse_args()

starting_date = args.sdate
ending_date = args.edate

# Get current date (in order to explore it, we need to leave
# ending_date = ending_date + 1 day:
if ending_date is None:
    ending_date = time.strftime("%Y-%m-%d") 
    c_y,c_m,c_d = ending_date.split('-')
    if int(c_d)+1 <= calendar.monthrange(int(c_y),int(c_m))[-1]:
        ending_date = c_y+'-'+c_m+'-'+str(int(c_d)+1)
    elif int(c_m)+1 <= 12:
        ending_date = c_y+'-'+str(int(c_m)+1)+'-01'
    else:
        ending_date = str(int(c_y)+1)+'-01-01'

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

# Get frame names from starting to ending date:
all_frame_names = np.array([])
all_frame_urls = np.array([])
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
        prop_frame_names = np.append(prop_frame_names,frame_names)
        prop_frame_urls = np.append(prop_frame_urls,frame_urls)
        c_y,c_m,c_d = edate.split('-')
        if int(c_y) == e_y and int(c_m) == e_m and int(c_d) == e_d:
            break
    print '\t Data collected for proposal '+prop+':'
    print '\t > Number of frames collected:',len(prop_frame_names)
    all_frame_names = np.append(all_frame_names,prop_frame_names)
    all_frame_urls = np.append(all_frame_urls,prop_frame_urls)

for i in range(len(all_frame_names)):
    framename = all_frame_names[i]
    frameurl = all_frame_urls[i]

    # Get date of current image frame:
    date = framename.split('-')[2]

    # Create new folder with the date if not already there:
    if not os.path.exists(datafolder+'/raw/'+date+'/'):
        os.mkdir(datafolder+'/raw/'+date+'/')

    # Check if file is already on folder. If not, download the file:    
    if not os.path.exists(datafolder+'/raw/'+date+'/'+framename):
        print '\t File '+framename+' not found on '+datafolder+'/raw/'+date+'/.'
        print '\t > Downloading ...'
        with open(datafolder+'/raw/'+date+'/'+framename,'wb') as f:
            f.write(requests.get(frameurl).content)
