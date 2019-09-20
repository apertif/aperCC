#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 13:07:00 2019

@author: kutkin
"""

import os
import numpy as np
from scipy.interpolate import interp1d
import casacore.tables as pt

import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

#TODO: plotting selected or all ants

import pyrap.measures as pm
import pyrap.quanta as qa
import ephem



def get_time(t):
    time_start = qa.quantity(t, 's')
    me = pm.measures()
    dict_time_start_MDJ = me.epoch('utc', time_start)
    time_start_MDJ=dict_time_start_MDJ['m0']['value']
    JD=time_start_MDJ+2400000.5-2415020
    d=ephem.Date(JD)
    return d.datetime()#.isoformat().replace("T","/")

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
            self.freq = freqs / 1e9 # GHz
            self.t0 = get_time(times[0])

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
        for a, ant in enumerate(ant_names[1:2]):
            fig, ax = plt.subplots(1,figsize=(4,3))
            plt.suptitle('Bandpass amplitude for Antenna {0}'.format(ant))
            ax.plot(self.freq[0,:],self.amp[a,:,0],
                            label='XX', ms=0.5, lw=0.3)
            ax.plot(self.freq[0,:],self.amp[a,:,1],
                            label='YY', ms=0.5, lw=0.3)
            ax.set_ylim(0,1.8)
            ax.legend(markerscale=3,fontsize=14)

    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""

        logging.info("Creating plots for bandpass phase")
        ant_names = self.ants
        for a,ant in enumerate(ant_names[:2]):
            plt.figure(figsize=(4,3))
            plt.suptitle('Bandpass phases for Antenna {0}'.format(ant))

            plt.plot(self.freq[0,:],self.phase[a,:,0],
                            label='XX', ms=0.5, lw=0.3)
            # plt.plot(self.freq[0,:],self.phase[a,:,1],
                            # label='YY', ms=0.5, lw=0.3)


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
        phase_norm = self.phase - other.phase

        return amp_norm, phase_norm


    def plot_norm_amp(self, other, ant='RT3', imagepath=None, ax=None):
        """Plot norm amplitude, one plot per antenna"""

        logging.info("Creating plots for normalized bandpass amplitude")
        amp_norm, phase_norm = self.normalize(other)
        a = self.ants.index(ant)
        if ax is None:
            fig, ax = plt.subplots(1)
        else:
            fig = ax.get_figure()

        ax.scatter(self.freq[0,:],amp_norm[a,:,0],
                        label='XX',
                        marker=',',s=1)
        ax.scatter(self.freq[0,:],amp_norm[a,:,1],
                        label='YY',
                        marker=',',s=1)

        ax.set_ylim(0.52,1.52)
        ax.set_xlim(1.22,1.53)
            # ax.legend(markerscale=3,fontsize=14)
        # if imagepath is not None:
            # fig.savefig('{}'.format(imagepath))


    def plot_norm_phase(self, other, ant='RT3', imagepath=None, ax=None):
        """Plot norm phase, one plot per antenna"""

        logging.info("Creating plots for bandpass phase")
        amp_norm, phase_norm = self.normalize(other)

        a = self.ants.index(ant)
        if ax is None:
            fig, ax = plt.subplots(1)
        else:
            fig = ax.get_figure()

        ax.scatter(self.freq[0,:], phase_norm[a,:,0],
                        label='XX',
                        marker=',',s=1)
        ax.scatter(self.freq[0,:], phase_norm[a,:,1],
                        label='YY',
                        marker=',',s=1)

        ax.set_ylim(-203,203)
        ax.set_xlim(1.22,1.53)


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
            self.t0 = get_time(times[0])
        else:
            logger.info('Gain table not present. Filling with NaNs.')
            self.amp = np.full((12,2,2),np.nan)
            self.phase = np.full((12,2,2),np.nan)
            self.ants = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
            self.time = np.full((2),np.nan)
            self.flags = np.full((12,2,2),np.nan)


    def normalize(self, other):
        """ divide by the other solutions """

        t1 = self.time - self.time[0]
        t2 = other.time - other.time[0]

        if len(t1) < len(t2):
            a1 = self.amp
            p1 = self.phase
            a2 = np.zeros_like(a1)
            p2 = np.zeros_like(p1)
            for a in range(len(self.ants)):
                for i in [0,1]: # XX and YY
                    a2[a,:,i] = np.interp(list(t1), list(t2), list(other.amp[a,:,i]))
                    p2[a,:,i] = np.interp(list(t1), list(t2), list(other.phase[a,:,i]))
            t = t1

        elif len(t1) > len(t2):
            a2 = other.amp
            p2 = other.phase
            a1 = np.zeros_like(a2)
            p1 = np.zeros_like(p2)
            for a in range(len(self.ants)):
                for i in [0,1]: # XX and YY
                    a1[a,:,i] = np.interp(list(t2), list(t1), list(self.amp[a,:,i]))
                    p1[a,:,i] = np.interp(list(t2), list(t1), list(self.phase[a,:,i]))
            t = t2
        else:
            a1 = self.amp
            p1 = self.phase
            a2 = other.amp
            p2 = other.phase
            t = t1



        amp_norm = a1 / a2
        phase_norm = p1 - p2

        return t/60, amp_norm, phase_norm

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

    def plot_norm_amp(self, other, ant='RT3', imagepath=None, ax=None):
        """Plot norm amplitude, one plot per antenna"""

        logging.info("Creating plots for gain amplitude")
        t, amp_norm, phase_norm = self.normalize(other)

        a = self.ants.index(ant)
        if ax is None:
            fig, ax = plt.subplots(1)
        else:
            fig = ax.get_figure()

        ax.scatter(t, amp_norm[a,:,0],
                   label='XX',
                   marker=',',s=5)
        ax.scatter(t, amp_norm[a,:,1],
                   label='YY',
                   marker=',',s=5)
        ax.set_ylim(0.18, 2.48)
        # print "AMP SHAPE:", amp_norm.shape

    def plot_norm_phase(self, other, ant='RT3', imagepath=None, ax=None):
        """Plot norm phase, one plot per antenna"""

        logging.info("Creating plots for bandpass phase")
        t, amp_norm, phase_norm = self.normalize(other)

        a = self.ants.index(ant)
        if ax is None:
            fig, ax = plt.subplots(1)
        else:
            fig = ax.get_figure()

        ax.scatter(t, phase_norm[a,:,0],
                        label='XX',
                        marker=',',s=1)
        ax.scatter(t, phase_norm[a,:,1],
                        label='YY',
                        marker=',',s=1)

        ax.set_ylim(-203, 203)
        # ax.set_xlim(1.22,1.53)

# test

a = BPSols('/home/kutkin/tmp/tmp/190807041_B03_3C147.Bscan')
a.plot_amp()
# a.plot_phase()
# plt.text(1.29, 1.65, '190807041')
# a.plot_phase()
# b = BPSols('/home/kutkin/apertif/pro/test_data/B03_3C196.Bscan')
# a.plot_norm_phase(b)

# a = GainSols('/home/kutkin/apertif/pro/test_data/B01_3C138.G1ap')

# a0 = GainSols('/home/kutkin/tmp/tmp/3C147.G1ap')
# a = GainSols('/home/kutkin/apertif/pro/test_data/3C196.G1ap')
# b = GainSols('/home/kutkin/apertif/pro/test_data/B03_3C138.G1ap')

# a = GainSols('/home/kutkin/tmp/tmp/B03_3C147.G1ap')
# b = GainSols('/home/kutkin/tmp/tmp/B00_3C147.G1ap')
# print a.amp.shape, b.amp.shape
# a.plot_norm_amp(b)
