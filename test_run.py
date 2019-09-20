#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:03:13 2019

@author: kutkin
"""

from modules.Sols import BPSols, GainSols
from modules.scandata import ScanData

import glob
import os
import re
import matplotlib.pyplot as plt

# def b2b(beams='all'):
#     """
#     Compare a beam to the same beam from other dataset
#     """

def get_fluxcal(obsid):
    """
    works only for a correctly processed data set
    """
    flst = glob.glob('/data/apertif/{}/00/raw/*.Bscan'.format(obsid))
    if not flst:
        return None
    bpsol = os.path.basename(flst[0])
    src = os.path.splitext(bpsol)[0]
    return src


def get_beam_num(pathstring):
    """return a string defining the beam number"""
    beamnum = re.findall('/(\d{2})/', pathstring)
    if beamnum:
        return beamnum[0]
    else:
        return None


def bpbeam(taskid, src, ants='all', datapath=None, plots=True):
    """
    Plot bandpass amplitude and phase per beam normalized by beam#00
    """
    SD = ScanData(taskid, src, base_dir=datapath, search_all_nodes=True)
    # print SD.get_bpasstable(0)

    BP0 = BPSols(SD.get_bpasstable(0))
    bps = SD.get_bpasstable()
    start_time = BP0.t0.isoformat()[:10] + ' ' + BP0.t0.isoformat()[11:16]

    nx = 8
    ny = 5
    xsize = nx*4
    ysize = ny*4

    if ants == 'all':
        antlist = BP0.ants
    elif type(ants) is str:
        antlist = [ants]
    elif type(ants) is list:
        antlist = ants

    # beamdict = dict()
    # antdict = dict()
    if plots:
        figs_amp = [plt.figure(figsize=(xsize,ysize)) for _ in antlist]
        figs_phase = [plt.figure(figsize=(xsize,ysize)) for _ in antlist]
    for bp in bps:
        beamnum = int(get_beam_num(bp))
        BP = BPSols(bp)
        for aind, ant in enumerate(antlist):
            if plots:
                fig1 = figs_amp[aind]
                fig2 = figs_phase[aind]
                ax1 = fig1.add_subplot(ny, nx, beamnum+1)
                ax2 = fig2.add_subplot(ny, nx, beamnum+1)
                BP.plot_norm_amp(BP0, ax=ax1, ant=ant, imagepath='bp_norm_{:02d}'.format(beamnum))
                BP.plot_norm_phase(BP0, ax=ax2, ant=ant, imagepath='bp_norm_{:02d}'.format(beamnum))
                if beamnum == 0:
                    ax1.legend()
                    ax2.legend()
                else:
                    ax1.text(0.85, 0.9, 'B{:02d}'.format(beamnum), fontsize=14, transform=ax1.transAxes)
                    ax2.text(0.85, 0.9, 'B{:02d}'.format(beamnum), fontsize=14, transform=ax2.transAxes)
    if plots:
        for ant, fig1, fig2 in zip(antlist, figs_amp, figs_phase):
            fig1.suptitle('Normalized BP amplitude {}, {}, {} ({})'.format(taskid, ant, src, start_time), fontsize=30)
            fig2.suptitle('Normalized BP phase {}, {}, {} ({})'.format(taskid, ant, src, start_time), fontsize=30)
            fig1.savefig('{}_BP_amp_{}.png'.format(taskid, ant))
            fig2.savefig('{}_BP_phase_{}.png'.format(taskid, ant))

        # antdict.update({ant:beamdict})
    # res = {taskid:[src, start_time, BP.freq, antdict]}

    # return res


def gbeam(taskid, src, ants='all', datapath=None, plots=False):
    """
    Get the gains for taskid->beam->antenna and
    [plot] gains amplitude and phase per beam normalized by beam 00
    """
    SD = ScanData(taskid, src, base_dir=datapath, search_all_nodes=True)
    # print SD.get_gaintable(0)

    G0 = GainSols(SD.get_gaintable(0))
    bps = SD.get_gaintable()
    start_time = G0.t0.isoformat()[:10] + ' ' + G0.t0.isoformat()[11:16]

    nx = 8
    ny = 5
    xsize = nx*4
    ysize = ny*4

    if ants == 'all':
        antlist = G0.ants
    else:
        antlist = ants

    if plots:
        figs_amp = [plt.figure(figsize=(xsize,ysize)) for _ in antlist]
        figs_phase = [plt.figure(figsize=(xsize,ysize)) for _ in antlist]

    for bp in bps:
        beamnum = int(get_beam_num(bp))
        G = GainSols(bp)
        for aind, ant in enumerate(antlist):
            if plots:
                fig1 = figs_amp[aind]
                fig2 = figs_phase[aind]
                if beamnum == 0:
                    fig1 = plt.figure(figsize=(xsize,ysize))
                    fig2 = plt.figure(figsize=(xsize,ysize))
                ax1 = fig1.add_subplot(ny, nx, beamnum+1)
                ax2 = fig2.add_subplot(ny, nx, beamnum+1)
                G.plot_norm_amp(G0, ax=ax1, ant=ant, imagepath='bp_norm_{:02d}'.format(beamnum))
                G.plot_norm_phase(G0, ax=ax2, ant=ant, imagepath='bp_norm_{:02d}'.format(beamnum))
                if beamnum == 0:
                    ax1.legend()
                    ax2.legend()
                else:
                    ax1.text(0.85, 0.9, 'B{:02d}'.format(beamnum), fontsize=14, transform=ax1.transAxes)
                    ax2.text(0.85, 0.9, 'B{:02d}'.format(beamnum), fontsize=14, transform=ax2.transAxes)
            # print taskid, start_time
        # fig.show()
    if plots:
        for ant, fig1, fig2 in zip(antlist, figs_amp, figs_phase):
            fig1.suptitle('Normalized Gain amplitude {}, {}, {} ({})'.format(taskid, ant, src, start_time), fontsize=30)
            fig2.suptitle('Normalized Gain phase {}, {}, {} ({})'.format(taskid, ant, src, start_time), fontsize=30)
            fig1.savefig('{}_G_amp_{}.png'.format(taskid, ant))
            fig2.savefig('{}_G_phase_{}.png'.format(taskid, ant))





if __name__ == "__main__":

    tasks = [
            '190809041',
            '190808041',
            '190807042',
            '190807041',
            '190806345',
            '190731125',
            '190728041',
            '190727042',
            '190727041',
            '190726041',
            '190725042',
            '190725041',
            '190722001',
            '190721041',
            '190720041',
            '190719042',
            '190719041',
            '190718124',
            '190714041',
            '190713042',
            '190713001',
            '190712041',
            '190711169',
            '190701042',
            '190701001'
            ]

    for task in tasks[-1:]:
        fluxcal = get_fluxcal(task)
        print task, fluxcal
        if fluxcal is not None:
            # try:
            res = bpbeam(task, fluxcal, ants=['RT3', 'RT4'], plots=True)
            # x = res[res.keys()[0]][3]
            # print x['RT3'][1][0]
            # plt.plot(res[res.keys()[0]][2][0,:], x['RT3'][1][0][0].T[0,:])
            # plt.show()
                # gbeam(task, fluxcal, ants='all')
            # except:
                # pass





    # src = '3C196'
    # datapath = '/data/apertif/'

