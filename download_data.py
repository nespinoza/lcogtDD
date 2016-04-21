# -*- coding: utf-8 -*-
import os
import time
import calendar
import requests
import numpy as np

################## USER OPTIONS ########################

# Starting date for which you want to check data from:
starting_date = '2016-04-01'

# End date (if None, then current date will be used):
ending_date = None

########################################################

# Get current date:
if ending_date is None:
    ending_date = time.strftime("%Y-%m-%d") 

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
            if frame['filename'].split('-')[-1] == 'e90.fits':
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
    print '\t > Number of frames:',len(prop_frame_names)
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
