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
