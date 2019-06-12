#!/usr/bin/env python

"""
Test script run preflag and prepare in apercc
"""

from aperCC.modules.apercc import apercc

# fluxcals = [(190410002, '3C196_0', 0), (190410003, '3C196_1', 1), (190410004, '3C196_2', 2), (190410005, '3C196_3', 3), (190410006, '3C196_4', 4),
#            (190410007, '3C196_5', 5), (190410008, '3C196_6', 6), (190410009, '3C196_7', 7), (190410010, '3C196_8', 8), (190410011, '3C196_9', 9)]

fluxcals = [[190410009, '3C196_7', 7], [190410010, '3C196_8', 8]

apercc(fluxcals, steps=['prepare', 'preflag', 'crosscal'])
