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

1. Fill in your LCOGT archive username, password, data folder and the name of 
   the proposals (separated by commas if there are more than one) for which you want 
   to check data on the `userdata.dat` file (the `datafolder` variable which you have 
   to fill is the data folder under which you want to download the LCOGT data. If you 
   already have LCOGT data, this folder should contain a folder called `raw` and, 
   inside, the frames ordered in sub-folders with the dates of these frames as names. 
   For example, if `datafolder = myfolder`, then the data for `20160416` is expected to be under
   `myfolder/raw/20160416/`). 

2. Select the dates between which you want to check data and fill them in the 
   `download_data.py` code. The only required input here is the starting date; if the 
   ending date is `None`, then the current date will be used and data will be downloaded 
   from the starting date to today for the given proposal.

3. Run the `download_data.py` code. This will download and save data from the starting 
   date to the end date.
