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
    def __init__(self, task_id, source_name, base_dir=None, use_all_nodes=False):
        """
        Initialize with task id and source name
        and place holders for phase and amplitude
        Args:
            task id (int): task id of data, e.g. 190303083
            source_name (str): name of source, e.g. "3C48"
            base_dir (str): name of data directory
            use_all_nodes (bool): Use data directories from all nodes, only affective on happili-01
        """

        # first check what happili node on
        self.hostname = os.uname()[1]

        # use data from all nodes
        self.use_all_nodes = use_all_nodes

        # main task id
        self.task_id = task_id

        # name of calibrator
        self.source_name = source_name

        if base_dir is None:
            self.base_dir = '/data/apertif/'
        else:
            self.base_dir = base_dir

        #self.imagepathsuffix = ""
        # Fix to not include .MS no matter what
        if self.source_name[-2:] == 'MS':
            self.source_name = self.source_name[:-3]

        # also get a directory list and beamlist
        self.task_id_path = os.path.join(self.base_dir, str(self.task_id))

        if self.hostname == 'happili-01' and use_all_nodes:
            self.dir_list = glob.glob(
                "{0}/[0-3][0-9]".format(self.task_id_path.replace("/data/", "/data*/")))
        else:
            self.dir_list = glob.glob(
                "{0}/[0-3][0-9]".format(self.task_id_path))

        if len(self.dir_list) == 0:
            logging.warning("No beam directories found")
        else:
            self.dir_list = np.array(self.dir_list)
            self.dir_list.sort()

        self.beam_list = np.array([os.path.basename(dir)
                                   for dir in self.dir_list])

        if len(self.beam_list) == 0:
            logging.warning("No beams found")

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
        if beam_nr is None:
            logging.info("Getting a list of gaintables")

            # empty table to be filled
            gaintable_list = []

            # go through directory list and check if table exists
            for single_dir in self.dir_list:
                gaintable = "{0}/raw/{1}.{2}".format(
                    single_dir, self.source_name, self.gaintable_suffix)
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
            # get the directory corresponding to the beam:
            data_dir = self.dir_list[np.where(
                self.beam_list == '{0:02d}'.format(beam_nr))]

            if len(data_dir) == 0:
                logging.warning(
                    "Could not find gaintable for beam {0:02d}".format(beam_nr))
                return -1
            else:
                data_dir = data_dir[0]

            gaintable = "{0}/raw/{1}.{2}".format(
                data_dir, self.source_name, self.gaintable_suffix)

            # gaintable = "{0}/{1:02d}/raw/{2}.{3}".format(
            #     self.task_id_path, beam_nr, self.source_name, self.gaintable_suffix)

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
        if beam_nr is None:
            logging.info("Getting a list of bandpass tables")

            # empty table to be filled
            bpass_list = []

            # go through directory list and check if table exists
            for single_dir in self.dir_list:
                bpass = "{0}/raw/{1}.{2}".format(
                    single_dir, self.source_name, self.bpass_suffix)
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
            # get the directory corresponding to the beam:
            data_dir = self.dir_list[np.where(
                self.beam_list == '{0:02d}'.format(beam_nr))]

            if len(data_dir) == 0:
                logging.warning(
                    "Could not find gaintable for beam {0:02d}".format(beam_nr))
                return -1
            else:
                data_dir = data_dir[0]

            bpass = "{0}/raw/{1}.{2}".format(
                data_dir, self.source_name, self.bpass_suffix)
            # bpass = "{0}/{1:02d}/raw/{2}.{3}".format(
            #     self.task_id_path, beam_nr, self.source_name, self.bpass_suffix)

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
