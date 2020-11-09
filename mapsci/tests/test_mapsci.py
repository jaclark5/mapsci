"""
Unit and regression test for the mapsci package.
"""

# Import package, test suite, and other packages as needed
import mapsci
import pytest
import sys
import os
import logging

logger = logging.getLogger(__name__)

temperature = 273 # [K]
bead_library = {
    "CO2": {'epsilon': 353.55, 'sigma': 3.741, 'lambdar': 23.0, 'lambdaa': 6.66, 'Sk': 1.0, 'charge': 0.0, 'dipole': 0.0, 'quadrupole': 4.62033, 'ionization_energy': 316.3969563680995, 'mass': 0.04401},
    "CH3": {'epsilon': 256.77, 'sigma': 4.0773, 'lambdar': 15.05, 'lambdaa': 6.0, 'Sk': 0.57255, 'charge': -0.03278, 'dipole': 0.068168573, 'quadrupole': 0.060537996, 'ionization_energy': 254.80129735161324,'mass': 0.01503}
}
bead_COO = {'epsilon': 341.02, 'sigma': 3.60, 'lambdar': 8.00, 'lambdaa': 6.0, 'Sk': 1.0, 'charge': -0.228231, 'dipole': 2.57943, 'quadrupole': 6.7388, 'ionization_energy': 231.975, 'mass': 0.04002}

def test_mapsci_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mapsci" in sys.modules

def test_mapsci_log_file():
    """Test enabling of logging"""
 
    mapsci.initiate_logger(log_file=True, verbose=10)

    logger = logging.getLogger(__name__)
    logger.info("test")

    if os.path.isfile("mapsci.log"):
        flag = True
        os.remove("mapsci.log")
    else:
        flag = False

    mapsci.initiate_logger(log_file=False)

    assert flag

def test_mapsci_log_console(capsys):
    """Test enabling of logging"""

    mapsci.initiate_logger(console=True, verbose=10)

    logger = logging.getLogger(__name__)
    logger.info("test")

    _, err = capsys.readouterr()

    mapsci.initiate_logger(console=False)
    assert "[INFO](mapsci.tests.test_mapsci): test" in err

def test_polarizability_analytical(bead_library=bead_library["CO2"], temperature=temperature):
    #   """Test ability to calculate polarizability"""
    output_library = mapsci.calc_polarizability(bead_library, temperature=temperature, calculation_method="analytical", distance_opts={"lower_bound": "tolerance"})
    pol_A = output_library["polarizability"]
    assert pol_A==pytest.approx(3.43,abs=1e-2)

def test_polarizability_failed_fitting(capsys, bead_library=bead_COO, temperature=335):
    #   """Test ability to calculate polarizability through fitting in the case where it fails"""
    mapsci.initiate_logger(console=True, verbose=10)
    output_library = mapsci.calc_polarizability(bead_library, temperature=temperature)

    pol_A = output_library["polarizability"]
    _, err = capsys.readouterr()

    mapsci.initiate_logger(console=False)
    assert pol_A==pytest.approx(0.00,abs=1e-2)
    assert "estimated polarizability" in err

def test_partial_polarizability(bead_library=bead_library["CO2"], temperature=temperature):
    #   """Test ability to calculate partial with respect to polarizability"""
    dalpha = mapsci.partial_polarizability(bead_library, temperature=temperature)
    assert dalpha["ionization_energy"]==pytest.approx(-0.03,abs=1e-2)
    assert dalpha["quadrupole"]==pytest.approx(-9142491041,abs=1e+2)

def test_curve_fit_cross_interactions(bead_library=bead_library, temperature=temperature):
    #   """Test ability to calculate cross interaction parameters"""
    dict_cross, _ = mapsci.extended_mixing_rules_fitting(bead_library, temperature, shape_factor_scale=True)
    eps = dict_cross["CO2"]["CH3"]["epsilon"]
    lambdaa = dict_cross["CO2"]["CH3"]["lambdaa"]
    lambdar = dict_cross["CO2"]["CH3"]["lambdar"]
    assert eps==pytest.approx(273.295,abs=1e-2) and lambdaa==pytest.approx(6.014,abs=1e-2) and lambdar==pytest.approx(18.599,abs=1e-2)

def test_analytical_cross_interactions(bead_library=bead_library, temperature=temperature):
    #   """Test ability to calculate cross interaction parameters"""
    dict_cross, _ = mapsci.extended_mixing_rules_analytical(bead_library, temperature, distance_opts={"lower_bound": "sigma"})

    eps = dict_cross["CO2"]["CH3"]["epsilon"]
    assert eps==pytest.approx(279.13,abs=1e-2)

def test_partial_energy_parameter(bead_library=bead_library, temperature=temperature):
    #   """Test ability to calculate partial with respect to cross interac†ion parameter"""
    depsilon = mapsci.partial_energy_parameter(bead_library["CO2"], bead_library["CH3"],temperature=temperature)
    print(depsilon)
    assert depsilon["1"]["ionization_energy"]==pytest.approx(9198084,abs=1e+2)
    assert depsilon["1"]["charge"]==pytest.approx(-6.08e+16, abs=1e+16)
    assert depsilon["1"]["dipole"]==pytest.approx(6.08e+29, abs=1e+29)
    assert depsilon["1"]["quadrupole"]==pytest.approx(2.21e+34,abs=1e+34)
    assert depsilon["1"]["polarizability"]==pytest.approx(3345081773707842,abs=1e+2)

def test_calc_self_mie_from_multipole(bead_dict=bead_library["CH3"], temperature=temperature):
    #   """Test calculation of Mie parameters from multipole moments"""
    bead_dict_new = mapsci.calc_self_mie_from_multipole(bead_dict, temperature=temperature)
    assert bead_dict_new["lambdaa"]==pytest.approx(5.9732, abs=1e-2)
    assert bead_dict_new["epsilon"]==pytest.approx(256.35, abs=1e-2)
    assert bead_dict_new["polarizability"]==pytest.approx(6.103, abs=1e-2)


