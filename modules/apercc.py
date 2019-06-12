# Module with main function for cross calibration test

__author__ = "R. Schulz, "
__date__ = "$11-Jun-2019 15:00:00$"
__version__ = "0.1"

import numpy as np
import os
import sys
#from scandata import ScanData
import apercal.libs.lib as lib
from time import time
import logging
from apercal.modules.prepare import prepare
from apercal.modules.preflag import preflag
from apercal.modules.ccal import ccal
from apercal.subs.managefiles import director


def apercc(cal_list=None, base_dir=None, task_id=None, cal_name=None, steps=None):
    """
    Main function to run the cross-calibration stability evaluation.

    For a list of calibrator scans or a given task id and calibrator name, 
    this functions runs the cross-calibration evaluation.
    The function can get the data from ALTA and flags them using the Apercal modules
    prepare and preflag. It compares the bandpass solutions and gain factors between beams
    and between observations of the same calibrators
    The different steps can be selected individually.

    Example:
        scanid, source name, beam: [190108926, '3C147_36', 36]
        steps: ['prepare', 'preflag', 'crosscal', bpass_compare', 'gain_comare', 'bpass_compare_obs', 'gain_compare_obs']
        function cal: apercc(cal_list=[[190108926, '3C147_36', 36], [190108927, '3C147_37', 37]) or apercc(task_id = 190409056, cal_name='3C196')

    Args:
        cal_list (List(List(int, str, int)): scan id, source name, beam, optional
        base_dir (str): Name of directory to store the data,
            if not specified it will be /data/apertif/<crosscal>/<scanid>
        task_id (int): ID of scan to be used as main ID and for the directory,
            if not specified it will be the first scan id
        cal_name (str): Name of the calibrator,
            if not specified the first name in the calibrator list will be used
        steps (List(str)): List of steps in this task

    To Do: Use existing data using the task_id option and the name of the calibrator?

    """

    # General setup
    # =============

    # start time of this function
    start_time = time()

    # check input
    # if no list of a calibrators is given
    if cal_list is None:
        # then it needs the task id and the calibrator name to look for existing data
        if task_id is not None and cal_name is not None:
            print("Using task id and calibrator name. Assuming to use existing data. Will not run preflag, prepare and crosscal")
            # check that if steps were provided, they don't contain preflag, prepare and crosscal
            if steps is not None:
                if 'prepare' in steps:
                    steps.remove('prepare')
                if 'preflag' in steps:
                    steps.remove('preflag')
                if 'crosscal' in steps:
                    steps.remove('crosscal')
            else:
                steps = ['bpass_compare', 'gain_comare',
                         'bpass_compare_obs', 'gain_compare_obs']
        # otherwise it won't do anything
        else:
            print(
                "Input parameters incorrect. Please specify either cal_list or task_id and cal_name. Abort")
            return -1
    else:
        print("Using list of calibrators")
        if not steps:
            steps = ['prepare', 'preflag', 'crosscal', 'bpass_compare',
                     'gain_comare', 'bpass_compare_obs', 'gain_compare_obs']

    # # check that preflag is in it if prepare is run
    # else:
    #     if 'prepare' in steps and not 'preflag' in steps:
    #         steps.insert(1, 'preflag')

    # get the scan id to be used as the task id
    if not task_id:
        task_id = cal_list[0][0]
    else:
        task_id = task_id

    # create data directory unless specified using the first id unless otherwise specified
    if not base_dir:
        base_dir = '/data/apertif/crosscal/{}/'.format(task_id)
    elif len(base_dir) > 0 and base_dir[-1] != '/':
        base_dir = base_dir + '/'
    if not os.path.exists(base_dir):
        try:
            os.mkdir(base_dir)
        except Exception as e:
            print("Creating the base directory failed. Abort")
            return -1

    logfilepath = os.path.join(base_dir, 'apercc.log')

    lib.setup_logger('debug', logfile=logfilepath)
    logger = logging.getLogger(__name__)
    # gitinfo = subprocess.check_output('cd ' + os.path.dirname(apercal.__file__) +
    #                                   '&& git describe --tag; cd', shell=True).strip()

    # logger.info("Apercal version: " + gitinfo)

    logger.info("Apertif cross-calibration stability evaluation")

    logger.debug("apercc called with argument cal_list={}".format(cal_list))
    logger.debug("steps = {}".format(steps))
    logger.debug("base_dir = {}".format(base_dir))
    logger.debug("task_id = {}".format(task_id))

    # number of calibrators
    n_cals = len(cal_list)

    # get the name of the flux calibrator
    if cal_name is None:
        name_cal = str(cal_list[0][1]).strip().split('_')[0]
    else:
        name_cal = cal_name

    # get a list of beams
    beam_list = np.array([cal_list[k][2] for k in range(n_cals)])

    # Getting the data using prepare
    # ==============================

    if "prepare" in steps:

        start_time_prepare = time()

        logger.info("Getting data for calibrators")

        # go through the list of calibrators and run prepare
        for (task_id_cal, name_cal, beamnr_cal) in cal_list:
            logger.info("Running prepare for {0} of beam {1}".format(
                name_cal, beamnr_cal))
            # create prepare object without config file
            prep = prepare(filename=None)
            # where to store the data
            prep.basedir = base_dir
            # give the calibrator as a target to prepare
            prep.fluxcal = ''
            prep.polcal = ''
            prep.target = name_cal.upper().strip().split('_')[0] + '.MS'
            prep.prepare_target_beams = str(beamnr_cal)
            prep.prepare_date = str(task_id_cal)[:6]
            prep.prepare_obsnum_target = str(task_id_cal)[-3:]
            try:
                prep.go()
            except Exception as e:
                logger.warning("Prepare failed for calibrator {0} ({1}) beam {2}".format(
                    str(task_id), name_cal, beamnr_cal))
                logger.exception(e)
            else:
                logger.info("Prepare successful for {0} of beam {1}".format(
                    name_cal, beamnr_cal))

        logger.info("Getting data for calibrators ... Done ({0:.0f}s)".format(
            time() - start_time_prepare))
    else:
        logger.info("Skipping getting data for calibrators")

    # Running preflag for calibrators
    # ===============================

    if 'preflag' in steps:
        start_time_flag = time()

        logger.info("Flagging data of calibrators")

        # Flag fluxcal (pretending it's a target)
        # needs to be changed for parallel preflag and make it a loop
        flag = preflag(filename=None)
        flag.basedir = base_dir
        flag.fluxcal = ''
        flag.polcal = ''
        flag.target = name_cal.upper().strip().split('_')[0] + '.MS'
        flag.beam = "{:02d}".format(beam_list[0])
        try:
            director(flag, 'rm', base_dir + '/param.npy',
                     ignore_nonexistent=True)
            flag.go()
        except Exception as e:
            logger.warning("Preflag failed")
            logger.exception(e)
        else:
            logger.info("Flagging data of calibrators ... Done ({0:.0f}s)".format(
                time() - start_time_flag))
    else:
        logger.info("Skipping running preflag for calibrators")

    # Running crosscal for calibrators
    # ===============================

    if 'crosscal' in steps:
        start_time_crosscal = time()

        logger.info("Running crosscal for calibrators")

        for beam_nr in beam_list:
            logger.info("Running crosscal for beam {0}".format(beam_nr))
            crosscal = ccal(file_=None)
            crosscal.basedir = base_dir
            crosscal.fluxcal = name_cal.upper().strip().split('_')[0] + '.MS'
            # p.polcal = name_to_ms(name_polcal)
            # p.target = name_to_ms(name_target)
            # p2.paramfilename = 'param_{:02d}.npy'.format(beamnr)
            crosscal.beam = "{:02d}".format(beam_nr)
            crosscal.crosscal_transfer_to_target = False
            # p2.crosscal_transfer_to_target_targetbeams = "{:02d}".format(
            #    beamnr)
            try:
                director(crosscal, 'rm', base_dir + '/param.npy',
                         ignore_nonexistent=True)
                # director(
                #     p2, 'rm', basedir + '/param_{:02d}.npy'.format(beamnr), ignore_nonexistent=True)
                crosscal.go()
            except Exception as e:
                # Exception was already logged just before
                logger.warning(
                    "Failed crosscal for beam {}".format(beam_nr))
                logger.exception(e)
            else:
                logger.info(
                    "Running crosscal for beam {0} ... Done".format(beam_nr))

        logger.info("Running crosscal for calibrators ... Done ({0:.0f}s)".format(
            time() - start_time_crosscal))
    else:
        logger.info("Skipping running crosscal for calibrators")

    # Running Bandbpass comparison
    # ============================

    if 'bpass_compare' in steps:

        start_time_prepare = time()

        logger.info("Comparing bandpass")

        logger.info("#### Doing nothing here yet ####")

        logger.info("Comparing bandpass ... Done ({0:.0f})".format(
            time() - start_time_prepare))
    else:
        logger.info("Skipping comparing bandpass")

    # Running Bandbpass comparison
    # ============================

    if 'gain_compare' in steps:

        start_time_gain = time()

        logger.info("Comparing gain solutions")

        logger.info("#### Doing nothing here yet ####")

        logger.info("Comparing gain solutions ... Done ({0:.0f})".format(
            time() - start_time_gain))
    else:
        logger.info("Skipping comparing gain solutions")

    # Running Bandbpass comparison between observations
    # =================================================
    if 'bpass_compare_obs' in steps:

        start_time_bandpass = time()

        logger.info("Comparing banpdass solutions across observations")

        logger.info("#### Doing nothing here yet ####")

        logger.info("Comparing banpdass solutions across observations ... Done ({0:.0f})".format(
            time() - start_time_bandpass))
    else:
        logger.info("Skipping comparing banpdass solutions across observations")

    # Running Bandbpass comparison between observations
    # =================================================
    if 'bpass_compare_obs' in steps:

        start_time_gain = time()

        logger.info("Comparing banpdass solutions across observations")

        logger.info("#### Doing nothing here yet ####")

        logger.info("Comparing banpdass solutions across observations ... Done ({0:.0f})".format(
            time() - start_time_gain))
    else:
        logger.info("Skipping comparing banpdass solutions across observations")

    logger.info(
        "Apertif cross-calibration stability evaluation ... Done ({0:.0f}s)".format(time() - start_time))
