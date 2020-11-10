"""
MAPSCI
MAPSCI: Multipole Approach of Predicting and Scaling Cross Interactions
"""

# Add imports here
from .multipole_mie_combining_rules import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions

import logging
import logging.handlers
import os

logger = logging.getLogger()
logger.setLevel(30)

def initiate_logger(console=False, log_file=None, verbose=30):
    """
    Initiate a logging handler if more detail on the calculations is desired.

    Parameters
    ----------
    console : bool, Optional, default=False
        Initiates a stream handler to print to a console
    log_file : bool/str, Optional, default=None
        If log output should be recorded in a file, set this keyword to either True or to a name for the log file. If True, the file name 'mapsci.log' is used. Note that if a file with the same name already exists, it will be deleted.
    verbose : int, Optional, default=30
        The verbosity of logging information can be set to any supported representation of the `logging level <https://docs.python.org/3/library/logging.html#logging-levels>`_.  
    """

    logger.setLevel(verbose)

    # Check for existing handlers
    handler_console = None
    handler_logfile = None
    for tmp in logger.handlers:
        if "RotatingFileHandler" in str(tmp):
            handler_logfile = tmp
        if "StreamHandler" in str(tmp):
            handler_console = tmp

    # Set up logging to console
    if console and handler_console == None:
        console_handler = logging.StreamHandler() # sys.stderr
        console_handler.setFormatter( logging.Formatter('[%(levelname)s](%(name)s): %(message)s') )
        console_handler.setLevel(verbose)
        logger.addHandler(console_handler)
    elif console:
        logger.warning("StreamHandler already exists")
    elif handler_console != None:
        logger.removeHandler(handler_console)

    # Rotating File Handler
    if log_file is not None and handler_logfile == None:
        
        if type(log_file) != str:
            log_file = "mapsci.log"

        if os.path.isfile(log_file):
            os.remove(log_file)

        log_file_handler = logging.handlers.RotatingFileHandler(log_file)
        log_file_handler.setFormatter( logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s') )
        log_file_handler.setLevel(verbose)
        logger.addHandler(log_file_handler)
    elif log_file:
        logger.warning("RotatingFileHandler already exists")
    elif handler_logfile != None:
        logger.removeHandler(handler_logfile)

