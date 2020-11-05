"""
Unit and regression test for the mapsci package.
"""

# Import package, test suite, and other packages as needed
import mapsci
import pytest
import sys

temperature = 273 # [K]
bead_library = {
    "CO2": {'epsilon': 353.55, 'sigma': 3.741, 'lambdar': 23.0, 'lambdaa': 6.66, 'Sk': 1.0, 'charge': 0.0, 'dipole': 0.0, 'quadrupole': 4.62033, 'ionization_energy': 316.3969563680995, 'mass': 0.04401},
    "CH3": {'epsilon': 256.77, 'sigma': 4.0773, 'lambdar': 15.05, 'lambdaa': 6.0, 'Sk': 0.57255, 'charge': -0.03278, 'dipole': 0.068168573, 'quadrupole': 0.060537996, 'ionization_energy': 254.80129735161324,'mass': 0.01503}
}

def test_mapsci_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mapsci" in sys.modules

def test_curve_fit_cross_interactions(bead_library=bead_library, temperature=temperature):
    #   """Test ability to calculate cross interaction parameters"""
    dict_cross, _ = mapsci.extended_mixing_rules_fitting(bead_library, temperature, shape_factor_scale=True)
    eps = dict_cross["CO2"]["CH3"]["epsilon"]
    lambdaa = dict_cross["CO2"]["CH3"]["lambdaa"]
    lambdar = dict_cross["CO2"]["CH3"]["lambdar"]
    assert eps==pytest.approx(273.295,abs=1e-2) and lambdaa==pytest.approx(6.014,abs=1e-2) and lambdar==pytest.approx(18.599,abs=1e-2)

def test_analytical_cross_interactions(bead_library=bead_library, temperature=temperature):
    #   """Test ability to calculate cross interaction parameters"""
    dict_cross, _ = mapsci.extended_mixing_rules_analytical(bead_library, temperature)
    eps = dict_cross["CO2"]["CH3"]["epsilon"]
    assert eps==pytest.approx(284.793,abs=1e-2)
