# aperCC: Cross-calibration solution stability for Apertif
# E. A. K. Adams

__author__ = "E.A.K. Adams"


"""
Script to get sets of calibrators scans, 
calibrate a reference set, 
apply solutions to all scan sets,
and examine stability of cross-calibration solutions
by looking at calibrated data.
Future development may add ability
to look at SEFDs or visualize calibration solutions
directly.
Takes a range of dates, center LO value
Optionally a taskid for a references scan

Usage: 
python aperCC <YYYY-MM-DD> <YYYY-MM-DD> <centfreq> -r ref

Requirements:
atdbquery in python path
"""

# import argparse
# #import numpy as np
# #from modules.functions import *

# #Argument parsing
# parser = argparse.ArgumentParser(
#          description='Look at cross-calibration solution stability')
# parser.add_argument("date1",help='Starting date for calibration scans',
#                     type=str)
# parser.add_argument("date2",help='Ending data for calibrator scans',type=str)
# parser.add_argument("centfreq",default=1370,
#                     help='Central frequency of observations',type=float)
# parser.add_argument('-r','--reference',default=None,type=str,
#                     help=('Taskid for a reference observation.'
#                           'Defaults to first calibrator observation'))
# args = parser.parse_args()


# Get the data
# Find sets of 40 beam calibrator scans
