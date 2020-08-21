"""
Unit and regression test for the mapsci package.
"""

# Import package, test suite, and other packages as needed
import mapsci
import pytest
import sys

def test_mapsci_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mapsci" in sys.modules
