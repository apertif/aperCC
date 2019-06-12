#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 13:07:00 2019

@author: kutkin
"""

import os
import numpy as np
import casacore.tables as pt

import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

#TODO: plotting selected or all ants

class BPSols():

    def __init__(self, bptable):
        self.bptable = bptable
        self.read_data()


    def read_data(self):

        if os.path.isdir(self.bptable):
            taql_command = ("SELECT TIME,abs(CPARAM) AS amp, arg(CPARAM) AS phase, "
                            "FLAG FROM {0}").format(self.bptable)
            t=pt.taql(taql_command)
            times = t.getcol('TIME')
            amp_sols=t.getcol('amp')
            phase_sols = t.getcol('phase')
            flags = t.getcol('FLAG')
            taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(self.bptable)
            t= pt.taql(taql_antnames)
            ant_names=t.getcol("NAME")
            taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(self.bptable)
            t = pt.taql(taql_freq)
            freqs = t.getcol('CHAN_FREQ')

            #check for flags and mask
            amp_sols[flags] = np.nan
            phase_sols[flags] = np.nan

            self.ants = ant_names
            self.time = times
            self.phase = phase_sols * 180./np.pi #put into degrees
            self.amp = amp_sols
            self.flags = flags
            self.freq = freqs

        else:
            logger.info('BP table not present. Filling with NaNs.')
            self.ants = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
            self.time = np.array(np.nan)
            self.phase = np.full((12,2,2),np.nan)
            self.amp = np.full((12,2,2),np.nan)
            self.freq = np.full((2,2),np.nan)


    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logging.info("Creating plots for bandpass amplitude")
        ant_names = self.ants
        for a, ant in enumerate(ant_names[:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Bandpass amplitude for Antenna {0}'.format(ant))
            plt.scatter(self.freq[0,:],self.amp[a,:,0],
                            label='XX',
                            marker=',',s=1)
            plt.scatter(self.freq[0,:],self.amp[a,:,1],
                            label='YY',
                            marker=',',s=1)
            plt.ylim(0,1.8)
            plt.legend(markerscale=3,fontsize=14)

    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""

        logging.info("Creating plots for bandpass phase")
        ant_names = self.ants
        for a,ant in enumerate(ant_names[:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Bandpass phases for Antenna {0}'.format(ant))

            plt.scatter(self.freq[0,:],self.phase[a,:,0],
                            label='XX',
                            marker=',',s=1)
            plt.scatter(self.freq[0,:],self.phase[a,:,1],
                            label='YY',
                            marker=',',s=1)

            plt.ylim(-180,180)
            plt.legend(markerscale=3,fontsize=14)


    def normalize(self, other):
        """
        multiply (divide) the solution by the other one.
        """

        if self.amp.shape != other.amp.shape:
            logger.warning('The shapes are different: {} vs {}'.\
                           format(self.amp.shape, other.amp.shape))

        amp_norm = self.amp / other.amp
        phase_norm = self.phase / other.phase

        return amp_norm, phase_norm


    def plot_norm_amp(self, other, imagepath=None):
        """Plot phase, one plot per antenna"""

        logging.info("Creating plots for normalized bandpass amplitude")

        amp_norm, phase_norm = self.normalize(other)

        # imagepath = self.create_imagepath(imagepath)
        ant_names = self.ants
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names[:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Bandpass amplitude (normalized) for Antenna {0}'.format(ant))

            plt.scatter(self.freq[0,:],amp_norm[a,:,0],
                            label='XX',
                            marker=',',s=1)
            plt.scatter(self.freq[0,:],amp_norm[a,:,1],
                            label='YY',
                            marker=',',s=1)

            plt.ylim(0,1.80)
            plt.legend(markerscale=3,fontsize=14)


class GainSols():
    def __init__(self, gaintable):
        self.gaintable = gaintable
        self.read_data()

    def read_data(self):
        #check if table exists
        #otherwise, place NaNs in place for everything
        if os.path.isdir(self.gaintable):
            taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(self.gaintable)
            t= pt.taql(taql_antnames)
            ant_names=t.getcol("NAME")

            #then get number of times
            #need this for setting shape
            taql_time =  "select TIME from {0} orderby unique TIME".format(self.gaintable)
            t= pt.taql(taql_time)
            times = t.getcol('TIME')

            #then iterate over antenna
            #set array sahpe to be [n_ant,n_time,n_stokes]
            #how can I get n_stokes? Could be 2 or 4, want to find from data
            #get 1 data entry
            taql_stokes = "SELECT abs(CPARAM) AS amp from {0} limit 1" .format(self.gaintable)
            t_pol = pt.taql(taql_stokes)
            pol_array = t_pol.getcol('amp')
            n_stokes = pol_array.shape[2] #shape is time, one, nstokes

            amp_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=object)
            phase_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=object)
            flags_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=bool)

            for ant in xrange(len(ant_names)):
                taql_command = ("SELECT abs(CPARAM) AS amp, arg(CPARAM) AS phase, FLAG FROM {0} "
                                "WHERE ANTENNA1={1}").format(self.gaintable,ant)
                t = pt.taql(taql_command)
                amp_ant_array[ant,:,:] = t.getcol('amp')[:,0,:]
                phase_ant_array[ant,:,:] = t.getcol('phase')[:,0,:]
                flags_ant_array[ant,:,:] = t.getcol('FLAG')[:,0,:]

            #check for flags and mask
            amp_ant_array[flags_ant_array] = np.nan
            phase_ant_array[flags_ant_array] = np.nan

            self.amp = amp_ant_array
            self.phase = phase_ant_array * 180./np.pi #put into degrees
            self.ants = ant_names
            self.time = times
            self.flags = flags_ant_array

        else:
            logger.info('Gain table not present. Filling with NaNs.')
            self.amp = np.full((12,2,2),np.nan)
            self.phase = np.full((12,2,2),np.nan)
            self.ants = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
            self.time = np.full((2),np.nan)
            self.flags = np.full((12,2,2),np.nan)


    def normalize(self, other):
        """ divide by the other solutions """

        amp_norm = self.amp / other.amp
        phase_norm = np.divide(self.phase, other.phase, out=np.zeros_like(self.phase), where=other.phase!=0)

        return amp_norm, phase_norm


    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logging.info("Creating plots for gain amplitude")
        ant_names = self.ants
        for a,ant in enumerate(ant_names[1:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Gain amplitude for Antenna {0}'.format(ant))
            plt.scatter(self.time,self.amp[a,:,0],
                       label='XX',
                       marker=',',s=5)
            plt.scatter(self.time,self.amp[a,:,1],
                       label='YY',
                       marker=',',s=5)
            plt.ylim(10,30)
            plt.legend(markerscale=3,fontsize=14)


    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""

        logging.info("Creating plots for gain phase")

        ant_names = self.ants
        for a, ant in enumerate(ant_names[1:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Gain phase for Antenna {0}'.format(ant))
            plt.scatter(self.time,self.phase[a,:,0],
                       label='XX',marker=',',s=5)
            plt.scatter(self.time,self.phase[a,:,1],
                       label='YY',marker=',',s=5)
            plt.ylim(-180,180)
            plt.legend(markerscale=3,fontsize=14)


    def plot_norm_amp(self, other):
        """Plot amplitude, one plot per antenna"""

        amp_norm, phase_norm = self.normalize(other)
        logging.info("Creating plots for gain amplitude")
        ant_names = self.ants

        for a,ant in enumerate(ant_names[1:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Gain amplitude for Antenna {0}'.format(ant))
            plt.scatter(self.time, amp_norm[a,:,0],
                       label='XX',
                       marker=',',s=5)
            plt.scatter(self.time, amp_norm[a,:,1],
                       label='YY',
                       marker=',',s=5)
            plt.ylim(0,1.8)
            plt.legend(markerscale=3, fontsize=7, loc=1)



