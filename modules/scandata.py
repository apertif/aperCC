import os
import numpy as np
import logging
import glob
import os
"""
Define object classes for holding data related to calibrator scans
for cross calibration evaluation

It needs the scan number name of the fluxcal (for cross-cal solutions)
Want to add functionality for pol-cal for pol solutions (secondary)
This specifies the location of all data, assuming setup of automatic pipeline
(/data/apertif, distributed across happili nodes)
"""


# def get_default_imagepath(scan):
#     """
#     Get the default path for saving images

#     Args:
#         scan (int): scan (or task id), e.g. 190303084

#     Returns:
#         str: Path for storing images
#     """
#     return '/data/apertif/{scan}/qa/'.format(scan=scan)


class ScanData(object):
    def __init__(self, scan, sourcename, base_dir):
        """
        Initialize with scan (taskid) and source name
        and place holders for phase and amplitude
        Args:
            scan (int): scan number, e.g. 190303083
            sourcename (str): name of source, e.g. "3C48"
            base_dir (str): name of data directory 
        """
        self.scan = scan
        self.sourcename = sourcename
        self.basedir = base_dir
        #self.imagepathsuffix = ""
        # Fix to not include .MS no matter what
        if self.sourcename[-2:] == 'MS':
            self.sourcename = self.sourcename[:-3]

        # also get a directory list and beamlist
        self.dir_list = glob.glob(
            "{0}{1}/[0-3][0-9]".format(self.basedir, self.scan))

        if len(self.dir_list) == 0:
            logging.warning("No beam directories found")

        self.beam_list = np.array([os.path.basename(dir)
                                   for dir in self.dir_list])

        if len(self.beam_list) == 0:
            logging.warning("No beams found")
        # first check what happili node on
        # if not happili-01, print a warning and only search locally
        self.hostname = os.uname()[1]

        # suffix used for the name of the gaintable
        self.gaintable_suffix = "G1ap"

        # suffix used for the name of the bandpass
        self.bpass_suffix = 'Bscan'

        # for path in paths:
        #     allfiles = os.listdir(path)
        #     for f in allfiles:
        #         full_path = os.path.join(path, f)
        #         if os.path.isdir(full_path) and len(f) == 2 and unicode(f, 'utf-8').isnumeric():
        #             self.dirlist.append(full_path)
        #             # create a list of all directories with full path.
        #             # This should be all beams - there should be no other directories
        #             # f is a string, so add to beam list to also track info about beams
        #             self.beamlist.append(f)

        # Initialize phase & amp arrays - common to all types of
        # self.phase = np.empty(len(self.dirlist), dtype=np.ndarray)
        # self.amp = np.empty(len(self.dirlist), dtype=np.ndarray)

    def get_gaintable(self, beam_nr=None):
        """
        Function to return the gaintable file if it exists.

        It is possible to specify a beam number. If a beam is not given,
        then a list of all gaintables will be returned

        Args:
            beam_nr (int): Number of beam, default looks for all beams
        """

        # if no beam is specified, return a list of tables
        if not beam_nr:
            logging.info("Getting a list of gaintables")

            # empty table to be filled
            gaintable_list = []

            # go through directory list and check if table exists
            for single_dir in self.dir_list:
                gaintable = "{0}/raw/{1}.{2}".format(
                    single_dir, self.sourcename, self.gaintable_suffix)
                if os.path.isdir(gaintable):
                    logging.info("Found gaintable {}".format(gaintable))
                    gaintable_list.append(gaintable)
                else:
                    logging.warning(
                        "Could not find gaintable {}".format(gaintable))

            if len(gaintable_list) == 0:
                logging.warning("No gaintables found")
                return -1
            else:
                return gaintable_list

        else:
            gaintable = "{0}{1:2d}/raw/{2}.{3}".format(
                self.basedir, beam_nr, self.sourcename, self.gaintable_suffix)

            if os.path.isdir(gaintable):
                logging.info("Found gaintable {}".format(gaintable))
                return gaintable
            else:
                logging.warning(
                    "Could not find gaintable {}".format(gaintable))
                return -1

    def get_bpasstable(self, beam_nr=None):
        """
        Function to return the bandpass table file if it exists.

        It is possible to specify a beam number. If a beam is not given,
        then a list of all bandpass tables will be returned

        Args:
            beam_nr (int): Number of beam, default looks for all beams
        """

        # if no beam is specified, return a list of tables
        if not beam_nr:
            logging.info("Getting a list of bandpass tables")

            # empty table to be filled
            bpass_list = []

            # go through directory list and check if table exists
            for single_dir in self.dir_list:
                bpass = "{0}/raw/{1}.{2}".format(
                    single_dir, self.sourcename, self.bpass_suffix)
                if os.path.isdir(bpass):
                    logging.info("Found bandpass table {}".format(bpass))
                    bpass_list.append(bpass)
                else:
                    logging.warning(
                        "Could not find bandpass table {}".format(bpass))

            if len(bpass_list) == 0:
                logging.warning("No bandpass tables found")
                return -1
            else:
                return bpass_list

        else:
            bpass = "{0}{1:2d}/raw/{2}.{3}".format(
                self.basedir, beam_nr, self.sourcename, self.bpass_suffix)

            if os.path.isdir(bpass):
                logging.info("Found bandpass table {}".format(bpass))
                return bpass
            else:
                logging.warning(
                    "Could not find bandpass table {}".format(bpass))
                return -1

    # def get_default_imagepath(self, scan):
    #     """
    #     Wrapper around get_default_imagepath, this can be overridden in scal, ccal with a suffix
    #     """
    #     return os.path.join(get_default_imagepath(scan), self.imagepathsuffix)

    # def create_imagepath(self, imagepath):
    #     """
    #     Create the image path. If imagepath is None, return a default one (and create it).

    #     Args:
    #         imagepath (str): path where images should be stored (e.g. "/data/dijkema/190303084" or None)

    #     Returns:
    #         str: image path that was created. Will be equal to input imagepath, or a generated path
    #     """
    #     if not imagepath:
    #         imagepath = self.get_default_imagepath(self.scan)

    #     if not os.path.exists(imagepath):
    #         logging.info("{} doesn't exist, creating".format(imagepath))
    #         os.makedirs(imagepath)

    #     return imagepath
