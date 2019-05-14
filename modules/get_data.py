#aperCC: modules for getting data for looking at CC solution stability
#E.A.K. Adams 15/05/2019

__author__="E.A.K. Adams"

"""
Functions related to getting data
for looking at crosscal solution stability
"""

from atdbquery import atdbquery
from datetime import datetime

def get_cal_scan_dict(centfreq,maxint=7,nskip=1,nswitch=30):
    """Use atdbquery to find all scans that are part of calibrator set
    Only include scans with correct centfreq
    Assume duration up to maxint minutes
    Can skip up to one scan (lost due to specification issues)
    And want at least nswitch scans (most of a set)
    """
    #query atdb
    allscans = atdbquery('imaging')
    #set up lists to hold taskids and names
    scanlist=[]
    namelist=[]
    #and set up dictionary to hold information at end
    switching_scan_dict = {}

    #iterate through scans
    #keep name and scan for those that are possibly interesting
    for scan in allscans:
        starttime = scan['starttime']
        endtime = scan['endtime']
        try:
            s1 = datetime.strptime(starttime,'%Y-%m-%dT%H:%M:%SZ')
            s2 = = datetime.strptime(endtime,'%Y-%m-%dT%H:%M:%SZ')
            length = s2-s1
        except TypeError:
            continue #restart loop if time is not string
        #identify short calibrator scans with correct centfreq
        if (scan['central_frequency'] == centfreq) and (length.seconds < maxint*60):
            scanlist.append(scan['taskID'])
            namelist.append(scan['name'])

    #this is a first pass list of possible calibrator scans
    #now sort the lists into scan order
    sorted_scan = sorted(scanlist)
    sorted_name = [name for _,name in sorted(zip(scanlist,namelist))]

    #iterate through lists and parse into subsets of calibrator scans
    tmpscanlist = []
    tmpnamelist = []
    tmpobslist = []
    for scan,name in zip(sorted_scan,sorted_name):
        #break name down
        name_split = name.split('_')
        #check for name structure and skip if not right:
        if len(name_split) == 2:
            
