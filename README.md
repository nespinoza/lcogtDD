lcogtDD
---------

Want to download data automatically from LCOGT? This is the python code to do it.

Dependencies
------------

The code needs the following libraries to be installed in order to work:

    - numpy (http://www.numpy.org/).
    - requests (http://docs.python-requests.org/en/master/).

Usage
-----

To use the code is simple: 

1. Fill in your LCOGT archive username and password on the `userdata.dat` file. 
   This will be read by the code in order to check for that. 

2. Select the dates between which you want to check data and fill them in the 
   `download_data.py` file, along with the name(s) of the proposal(s) that you want 
   to check data from. Also fill in the `datafolder` variable which is the data folder 
   under which you want to download the LCOGT data. If you already have LCOGT data, 
   this folder should contain another folder called `raw` and, inside, the frames 
   ordered in sub-folders with the dates of these frames. For example, if 
   `datafolder = 'myfolder'`, then the data for `20160404` is expected to be under 
   `myfolder/raw/20160404/`.

3. Run the `download_data.py` code. This will download and save data from the starting 
   date to the end date.
