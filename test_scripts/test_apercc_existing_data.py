#!/usr/bin/env python

"""
Test script run preflag and prepare in apercc
"""

from aperCC.modules.apercc import apercc

# fluxcals = [(190409025, '3C138_9', 9), (190409024, '3C138_8', 8), (190409023, '3C138_7', 7), (190409022, '3C138_6', 6), (190409021, '3C138_5', 5),
#             (190409020, '3C138_4', 4), (190409019, '3C138_3', 3), (190409018, '3C138_2', 2), (190409017, '3C138_1', 1), (190409016, '3C138_0', 0)]

fluxcals = [[190409024, '3C138_8', 8], [190409023, '3C138_7', 7]]

apercc(task_id=190409024, cal_name='3C138', steps=['crosscal'])
