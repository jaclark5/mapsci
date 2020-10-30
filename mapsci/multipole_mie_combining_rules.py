"""

MAPSCI: Multipole Approach of Predicting and Scaling Cross Interactions

Handles the primary functions
"""

import numpy as np
import scipy.optimize as spo
import logging

logger = logging.getLogger(__name__)


def calc_distance_array(bead_dict, tol=0.01, max_factor=2, lower_bound="rmin"):
    r"""
    Calculation of array for nondimensionalized distance array.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    bead_dict : dict
        Dictionary of multipole parameters.
        
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    tol : float, Optional, default: 0.01
        Ratio of absolute value of repulsive over attractive term of the Mie potential to define minimum bound
    max_factor : int, Optional, default: 2
        Factor to multiply minimum bound by to define maximum bound.
    lower_bound : str, Optional, default='rmin'
        Lower bound of distance array. Can be one of:

        - rmin: the position of the potential well
        - sigma: the size parameter
        - tolerance: Uses 'tol' keyword to define the ratio between the attractive and repulsive terms of the Mie potential, note that if tol = 0.01 the lower bound will be ~2.5*sigma.
    
    Returns
    -------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    """

    if lower_bound == "rmin":
        rm = mie_potential_minimum(bead_dict)
    elif lower_bound == "sigma":
        rm = bead_dict["sigma"]
    elif lower_bound == "tolerance":
        rm = bead_dict["sigma"] * (1 / tol)**(1 / (bead_dict["lambdar"] - bead_dict["lambdaa"]))

    r_array = np.linspace(rm, max_factor * rm, num=10000)

    return r_array


def mie_potential_minimum(bead_dict):
    r"""

    Parameters
    ----------
    bead_dict : dict
        Dictionary of multipole parameters.
        
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    Returns
    -------
    rmin : float
        Position of minimum of potential well
    """

    return bead_dict["sigma"] * (bead_dict["lambdar"] / bead_dict["lambdaa"])**(1 / (bead_dict["lambdar"] - bead_dict["lambdaa"]))


def mixed_parameters(bead1, bead2):
    r"""
    Calculate basic mixed parameters, where the energy parameter is calculated with the geometric mean

    Parameters
    ----------
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    Returns
    -------
    beadAB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
    """

    beadAB = {}
    beadAB["sigma"] = (bead1["sigma"] + bead2["sigma"]) / 2
    beadAB["lambdar"] = 3 + np.sqrt((bead1["lambdar"] - 3) * (bead2["lambdar"] - 3))
    beadAB["lambdaa"] = 3 + np.sqrt((bead1["lambdaa"] - 3) * (bead2["lambdaa"] - 3))
    beadAB["epsilon"] = np.sqrt(bead1["epsilon"] * bead2["epsilon"])

    return beadAB


def calc_mie_attractive_potential(r, bead_dict):
    r"""
    Calculation of nondimensionalized Mie potential.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    bead_dict : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor
    
    Returns
    -------
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads from Mie potential. Array is equal in length to "r". :math:`\phi'=\phi/(3k_{B}T)`
    """

    potential = -prefactor(bead_dict["lambdar"], bead_dict["lambdaa"]) * bead_dict["epsilon"] * (bead_dict["sigma"] /
                                                                                         r)**bead_dict["lambdaa"]

    return potential


def prefactor(lamr, lama):
    """ Calculation prefactor for Mie potential
    """

    return lamr / (lamr - lama) * (lamr / lama)**(lama / (lamr - lama))


def calc_lambdaij_from_epsilonij(epsij, bead1, bead2):
    r"""
    Calculates cross-interaction exponents from cross interaction energy parameter

    Parameters
    ----------
    epsilonij : float
        Fit energy parameter from multipole combining rules

    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    Returns
    -------
    lambdar_new : float
        Repulsive exponent
    lambdaa_new : float
        Attractive exponent 
    """

    sigmaij = np.mean([bead1["sigma"], bead2["sigma"]])
    tmp = epsij * sigmaij**3 / np.sqrt(bead1["sigma"]**3 * bead2["sigma"]**3) / np.sqrt(
        bead1["epsilon"] * bead2["epsilon"])
    lamr_ij = 3 + tmp * np.sqrt((bead1["lambdar"] - 3) * (bead2["lambdar"] - 3))
    lama_ij = 3 + tmp * np.sqrt((bead1["lambdaa"] - 3) * (bead2["lambdaa"] - 3))

    return lamr_ij, lama_ij


def calc_epsilonij_from_lambda_aij(lambda_a, bead1, bead2):
    r"""
    Calculate cross-interaction exponents from cross interaction energy parameter

    Parameters
    ----------
    lambda_aij : float
        Mixed attractive exponent from multipole combining rules
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    Returns
    -------
    lambdar_new : float
        Repulsive exponent
    lambdaa_new : float
        Attractive exponent 
    """

    tmp_sigma = np.sqrt(bead1["sigma"]**3 * bead2["sigma"]**3) / np.mean([bead1["sigma"], bead2["sigma"]])**3
    tmp_lambda = (lambda_a - 3) / np.sqrt((bead1["lambdaa"] - 3) * (bead2["lambdaa"] - 3))
    epsilon_ij = np.sqrt(bead1["epsilon"] * bead2["epsilon"]) * tmp_sigma * tmp_lambda

    return epsilon_ij


def calc_lambdarij_from_lambda_aij(lambda_a, alpha_mie):
    r"""
    Calculate cross-interaction repulsive exponent from cross interaction attractive exponent and Mie 'vdW like' interaction parameter.

    Parameters
    ----------
    lambda_aij : float
        Mixed attractive exponent from multipole combining rules
    alpha_mie : float
        This nondimensionalized attractive parameter for the Mie potential is related not only to the Mie exponents but also to the triple and critical temperatures of a substance.  

    Returns
    -------
    lambdar_new : float
        Repulsive exponent
    """

    lambda_r = spo.brentq(lambda x: alpha_mie - prefactor(x, lambda_a) * (1 / (lambda_a - 3) - 1 / (x - 3)),
                          lambda_a * 1.01,
                          1e+4,
                          xtol=1e-12)

    return lambda_r


def calc_self_multipole_potential(r, polarizability, *, charge, dipole, quadrupole, ionization_energy):
    r"""
    Calculation of nondimensionalized self-interaction potential using extended multipole expression.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    polarizability : float
        Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
    charge : float
        Nondimensionalized charge of bead. :math:`q'=q/e`
    dipole : float
        Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
    quadrupole : float
        Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
    ionization_energy : float
        Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    Returns
    -------
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads based on multipole components. Array is equal in length to "r". :math:`\phi'=\phi/(3k_{B}T)`

    """

    t11 = -charge**2 * dipole**2
    t12 = -charge**2

    t21 = -3 * ionization_energy / 4
    t22 = -2 * dipole**2
    t23 = -dipole**4 - 3 * quadrupole**2 * charge**2 / 5

    t31 = -3 * dipole**2 * quadrupole**2
    t32 = -3 * quadrupole**2

    t41 = -21 / 5 * quadrupole**4

    potential = (t11 + polarizability*t12)/r**4 \
              + (t21*polarizability**2 + t22*polarizability + t23)/r**6 \
              + (t31 + polarizability*t32)/r**8 \
              + t41/r**10

    return potential


def fit_polarizability(r, bead_dict, tol=0.05, shape_factor_scale=False, plot_fit=False):
    r"""
    Calculation of nondimensionalized polarizability by fitting the sum of multipole potentials to attractive term of Mie potential.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    bead_dict : dict
        Dictionary of multipole parameters.
        
        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    tol : float, Optional, default: 0.01
        Ratio of variance over polarizability value from curve-fit
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    plot_fit : bool, Optional, default: False
        Plot Mie potential and Multipole potential for comparison.
    
    Returns
    -------
    Polarizability : float
        Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
    """

    bead_dict_new = bead_dict.copy()
    if shape_factor_scale and "Sk" in bead_dict_new:
        bead_dict_new["epsilon"] = bead_dict_new["epsilon"] * bead_dict_new["Sk"]**2

    w_mie = calc_mie_attractive_potential(r, bead_dict_new)

    p0 = [1.e-6]
    pol_tmp, var_matrix = spo.curve_fit(
        lambda x, a: calc_self_multipole_potential(x,
                                                   a,
                                                   charge=bead_dict_new["charge"],
                                                   dipole=bead_dict_new["dipole"],
                                                   quadrupole=bead_dict_new["quadrupole"],
                                                   ionization_energy=bead_dict_new["ionization_energy"]),
        r,
        w_mie,
        p0=p0,
        bounds=(0.0, np.inf))

    if np.diag(var_matrix) / pol_tmp > tol:
        _ = test_polarizability(pol_tmp, bead_dict_new, r, plot_fit=plot_fit)

    return pol_tmp[0], var_matrix[0][0]


def test_polarizability(polarizability, bead_dict, r, plot_fit=False):
    r"""
    If polarizability doesn't provide a good fit between multipole potential and Mie potential, use estimated polarizability to suggest a different attractive exponent and energy parameter.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    polarizability : float
        Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
    bead_dict : dict
        Dictionary of multipole parameters.
        
        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    plot_fit : bool, Optional, default: False
        Plot Mie potential and Multipole potential for comparison.
    
    Returns
    -------
    epsilon_fit : float
        Energy parameter with curve fit against multipole potential using fit polarizability
    """

    bead_dict_new = bead_dict.copy()

    bead_dict_new["polarizability"] = polarizability
    output = fit_multipole_cross_interaction_parameter(bead_dict_new, bead_dict_new, distance_array=r)

    logger.info(
        "Refitting attractive exponent with estimated polarizability of {} yields: lamba_a {}, epsilon {}".format(
            bead_dict_new["polarizability"], output["lambdaa_fit"], output["epsilon_fit"]))

    if plot_fit:
        try:
            import matplotlib.pyplot as plt
        except:
            logger.error("Package matplotlib is not available")
            plot_fit = False
        if plot_fit:
            w_mie = calc_mie_attractive_potential(r, bead_dict_new)
            bead_dict_plot = bead_dict_new.copy()
            bead_dict_plot.update({"epsilon": output["epsilon_fit"], "lambdaa": output["lambdaa_fit"]})
            w_mie_fit = calc_mie_attractive_potential(r, bead_dict_plot)
            plt.figure(1)
            plt.plot(r, w_mie, "--k", label="Mie")
            plt.plot(r, w_mie_fit, "--r", label="Mie fit")
            multipole_terms = calc_cross_multipole_terms(bead_dict_new, bead_dict_new)
            logger.debug(
                "charge-dipole, charge-induced_dipole, induced_dipole-induced_dipole, dipole-dipole, dipole-induced_dipole, charge-quadrupole, dipole-quadrupole, induced_dipole-quadrupole, quadrupole-quadrupole"
            )
            logger.debug(multipole_terms, "\n\n")
            potential, potential_terms = calc_cross_multipole_potential(r, multipole_terms, total_only=False)
            plot_multipole_potential(r, potential, potential_terms=potential_terms)

    return output["epsilon_fit"]


def calc_cross_multipole_terms(beadA, beadB):
    r"""
    Calculation of terms for nondimensionalized cross-interaction potential from multipole moments.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - polarizability (float) Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - polarizability (float) Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    Returns
    -------
    multipole_terms : numpy.ndarray
        This list of nine terms terms corresponds to the coefficients the various multipole interactions: charge-dipole, charge-induced_dipole, induced_dipole-induced_dipole, dipole-dipole, dipole-induced_dipole, charge-quadrupole, dipole-quadrupole, induced_dipole-quadrupole, quadrupole-quadrupole
    """

    t11 = (beadA['charge']**2. * beadB['dipole']**2 + beadB['charge']**2. * beadA['dipole']**2.) / 2.0
    t12 = (beadA['charge']**2. * beadB['polarizability'] + beadB['charge']**2. * beadA['polarizability']) / 2.0

    I = beadA['ionization_energy'] * beadB['ionization_energy'] / (beadA['ionization_energy'] +
                                                                   beadB['ionization_energy'])

    t21 = 3. * I * beadA['polarizability'] * beadB['polarizability'] / 2.
    t22 = beadA['dipole']**2. * beadB['dipole']**2.
    t23 = beadA['polarizability'] * beadB['dipole']**2. + beadB['polarizability'] * beadA['dipole']**2.
    t24 = 3. * (beadA['quadrupole']**2. * beadB['charge']**2. + beadB['quadrupole']**2. * beadA['charge']**2.) / 10.

    t31 = 3. / 2. * (beadA['dipole']**2. * beadB['quadrupole']**2. + beadB['dipole']**2. * beadA['quadrupole']**2.)
    t32 = 3. / 2. * (beadA['quadrupole']**2. * beadB['polarizability'] +
                     beadB['quadrupole']**2. * beadA['polarizability'])

    t41 = 21. / 5. * beadA['quadrupole']**2. * beadB['quadrupole']**2.

    multipole_terms = np.array([t11, t12, t21, t22, t23, t24, t31, t32, t41])

    return multipole_terms


def condense_multipole_terms(multipole_terms):
    r"""
    The various multipole interactions take place at various orders of distances, ranging from r^(-4) to r^(-10) by orders of 2. This function will take the output of ``calc_cross_multipole_terms`` and combine the appropriate terms to produce 4 coefficients, one for each order of r.
        
    Parameters
    ----------
    multipole_terms : numpy.ndarray
        This list of nine terms terms corresponds to the coefficients the various multipole interactions: charge-dipole, charge-induced_dipole, induced_dipole-induced_dipole, dipole-dipole, dipole-induced_dipole, charge-quadrupole, dipole-quadrupole, induced_dipole-quadrupole, quadrupole-quadrupole

    Returns
    -------
    new_multipole_terms : numpy.ndarray
        This list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, respectively.
    """

    new_multipole_terms = np.zeros(4)

    new_multipole_terms[0] = np.sum(multipole_terms[:1])
    new_multipole_terms[1] = np.sum(multipole_terms[2:6])
    new_multipole_terms[2] = np.sum(multipole_terms[6:8])
    new_multipole_terms[3] = np.sum(multipole_terms[8])

    return new_multipole_terms


def calc_cross_multipole_potential(r, multipole_terms, total_only=True):
    r"""
    Calculation of nondimensionalized cross-interaction potential from multipole moments.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    multipole_terms : numpy.ndarray
        This can be either a list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, or a list of nine terms terms corresponding to the coefficients the various multipole interactions.
    total_only : bool, Optional, default: True
        If true, only the overall potential is returned. This is useful for parameter fitting. If False, the potential for each term is returned in a numpy array.
    
    Returns
    -------
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads based on multipole moments. Array is equal in length to "r". :math:`\phi'=\phi/(3k_{B}T)`
    potential_terms : numpy.ndarray, Optional
        2D array of terms involved in multipole moment. Could be 4 terms relating to orders of r from -4 to -10 by steps of 2, or could be the individual contributions.
        Only provided if ``total_only`` is False
    """

    if np.size(multipole_terms) == 4:
        potential_terms = np.array([
            -multipole_terms[0] / r**4., -multipole_terms[1] / r**6., -multipole_terms[2] / r**8.,
            -multipole_terms[3] / r**10.
        ])
    elif np.size(multipole_terms) == 9:
        potential_terms = np.array([
            -multipole_terms[0] / r**4., -multipole_terms[1] / r**4., -multipole_terms[2] / r**6.,
            -multipole_terms[3] / r**6., -multipole_terms[4] / r**6., -multipole_terms[5] / r**6.,
            -multipole_terms[6] / r**8., -multipole_terms[7] / r**8., -multipole_terms[8] / r**10.
        ])
    else:
        raise ValueError(
            "Multipole terms input should be either of length 4 or length 9 for the supported interaction types.")

    potential = np.sum(potential_terms, axis=0)

    if total_only:
        return potential
    else:
        return potential, potential_terms


def plot_multipole_potential(r, potential, potential_terms=None, show=True):
    r"""
    Plot multipole potential and each contribution (if provided).
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads based on multipole moments. Array is equal in length to "r". :math:`\phi'=\phi/(3k_{B}T)`
    multipole_terms : numpy.ndarray
        This can be either a list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, or a list of nine terms terms corresponding to the coefficients the various multipole interactions.
    """

    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:
        plt.figure(1, figsize=(4, 4))
        plt.xlabel("Dimensionless Distance")
        plt.ylabel("Dimensionless Potential")

        plt.plot(r, potential, label="Total")
        if potential_terms is not None:
            if np.shape(potential_terms)[0] == 4:
                plt.plot(r, potential_terms[0], label="O(-4)")
                plt.plot(r, potential_terms[1], label="O(-6)")
                plt.plot(r, potential_terms[2], label="O(-8)")
                plt.plot(r, potential_terms[3], label="O(-10)")
            elif np.shape(potential_terms)[0] == 9:
                # dipole-quadrupole, induced_dipole-quadrupole, quadrupole-quadrupole
                plt.plot(r, potential_terms[0], label=r"$q-\mu$")
                plt.plot(r, potential_terms[1], label=r"$q-\mu_{induced}$")
                plt.plot(r, potential_terms[2], label=r"$\mu_{induced}-\mu_{induced}$")
                plt.plot(r, potential_terms[3], label=r"$\mu-\mu$")
                plt.plot(r, potential_terms[4], label=r"$\mu-\mu_{induced}$")
                plt.plot(r, potential_terms[5], label=r"$q-Q$")
                plt.plot(r, potential_terms[6], label=r"$\mu-Q$")
                plt.plot(r, potential_terms[7], label=r"$\mu_{induced}-Q$")
                plt.plot(r, potential_terms[8], label=r"$Q-Q$")
            else:
                raise ValueError(
                    "Multipole terms input should be either of length 4 or length 9 for the supported interaction types.")
            plt.legend(loc="best")

        plt.tight_layout()
        if show:
            plt.show()


def solve_polarizability_integral(sigma0, bead_dict0, shape_factor_scale=False):
    r"""
    Calculation of nondimensionalized polarizability from multipole moments using integral method.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    sigma0 : float
        This lower bound of the integral dictates where we expect to start matching the multipole attractive term with that of Mie potential. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    bead_dict : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    
    Returns
    -------
    polarizability : float
        Polarizability calculated from Mie and multipole potentials, integrated over all space
    """

    bead_dict = bead_dict0.copy()
    if shape_factor_scale:
        if "Sk" in bead_dict:
            bead_dict["epsilon"] = bead_dict["epsilon"] * bead_dict["Sk"]**2
        else:
            raise ValueError("Shape factor was not provided in bead dictionary")
    Cmie_int = mie_integral(sigma0, bead_dict)

    tmp1 = _obj_polarizability_from_integral(np.finfo("float").eps, bead_dict, Cmie_int, sigma0)
    tmp2 = _obj_polarizability_from_integral(1, bead_dict, Cmie_int, sigma0)
    if tmp1 * tmp2 < 0:
        polarizability = spo.brentq(_obj_polarizability_from_integral,
                                    np.finfo("float").eps,
                                    1,
                                    args=(bead_dict, Cmie_int, sigma0),
                                    xtol=1e-12)
    else:
        polarizability = np.nan

    return polarizability


def _obj_polarizability_from_integral(polarizability, bead_dict, Cintegral, sigma0):
    r"""
    Objective function used to determine the polarizability from multipole and Mie integrals from some minimum to infinity
    
    Parameters
    ----------
    epsilon : float
        Guess in nondimensionalized energy parameter in [kcal/mol], math:`\epsilon'=\epsilon/(3k_{B}T)`
    bead_dict : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    Cintegral : float
        This sum of the multipole integrals is set equal to the attractive term of the integrated Mie potential to determine the energy parameter.
    sigma0 : float
        Nondimensionalized value of the lower bound of the integral

    Returns
    -------
    obj_value : float
        Difference between multipole term and Mie potential term integral
    """

    dict_tmp = bead_dict.copy()
    dict_tmp["polarizability"] = polarizability

    Cmultipole, _ = multipole_integral(sigma0, dict_tmp, dict_tmp)

    return Cmultipole - Cintegral


def partial_polarizability(bead_dict0, temperature=None, sigma0=None, lower_bound="rmin"):
    r"""
    Calculate partial derivative with respect to multipole moments.
    
    Parameters
    ----------
    bead_dict : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) [K] Energy parameter scaled by Boltzmann constant
        - sigma (float) [Angstroms] Size parameter
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) [Angstroms^3] This quantity is used as a free parameter in mixing rule
        - charge (float) [-] Charge of bead fragment in elementary charges
        - dipole (float) [Debye] Dipole moment of bead fragment
        - quadrupole (float) [Debye*Angstroms] Quadrupole moment of bead fragment
        - ionization_energy (float) [kcal/mol] Ionization energy of bead fragment

    temperature : float, Optional, default=298
        Temperature of the system.
    sigma0 : float, Optional, default=None
        In angstroms, this lower bound of the integral dictates where the lower bound of the definite integral is
    lower_bound : str, Optional, default='rmin'
        Lower bound of distance array. Used only when sigma0 is None. Can be one of:

        - rmin: the position of the potential well
        - sigma: the size parameter
    
    Returns
    -------
    partial_dict : dict
        Partial derivative with respect to multipole moments
    """

    if temperature is None:
        temperature = 298
        logger.info("Using default temperature of 298 K")

    tmp = {"bead": bead_dict0.copy()}
    bead_dict = dict_dimensions(tmp, temperature, dimensions=False)["bead"]

    if sigma0 is None:
        if lower_bound == "rmin":
            rm = mie_potential_minimum(bead_dict)
        elif lower_bound == "sigma":
            rm = bead_dict["sigma"]
    else:
        rm = sigma0

    a = -2 / bead_dict['ionization_energy'] * (bead_dict['charge']**2. * rm**2 + 2 * bead_dict['dipole']**2 / 3 +
                                               3 * bead_dict['quadrupole']**2.0 * rm**2)
    b = 4 / bead_dict['ionization_energy']**2 * (
        bead_dict['charge']**4. * rm**4 + 4 * bead_dict['charge']**2. * bead_dict['dipole']**2 * rm**2 / 3 +
        6 * bead_dict['quadrupole']**2. * bead_dict['charge']**2. / 5 + 4 / 9 * bead_dict['dipole']**4 + 4 / 5 *
        bead_dict['dipole']**2 * bead_dict['quadrupole']**2.0 / rm**2 + 9 / 25 * bead_dict['quadrupole']**4.0 / rm**4)
    c = 4 / bead_dict['ionization_energy'] * (
        bead_dict['charge']**2. * bead_dict['dipole']**2 * rm**2 + bead_dict['dipole']**4 / 3 +
        bead_dict['quadrupole']**2. * bead_dict['charge']**2. / 5 +
        3 / 5 * bead_dict['quadrupole']**2. * bead_dict['dipole']**2. / rm**2 +
        3 / 5 * bead_dict['quadrupole']**4.0 / rm**4 - prefactor(bead_dict['lambdar'], bead_dict['lambdaa']) /
        (bead_dict['lambdaa'] - 3) * bead_dict['epsilon'] * bead_dict['sigma']**bead_dict['lambdaa'] / rm**
        (bead_dict['lambdaa'] - 6))

    partial_dict = {}
    for key in bead_dict0:
        if key == "ionization_energy":
            partial_dict[key] = -(a + np.sqrt(b - c)) / bead_dict['ionization_energy']
        elif key == "charge":
            tmp1 = 4 / bead_dict['ionization_energy']**2 * (
                4 * bead_dict['charge']**3 * rm**4 + 8 / 3 * bead_dict['charge'] * bead_dict['dipole']**2 * rm**2 +
                bead_dict['charge'] * bead_dict['quadrupole']**2 * 12 / 5)
            tmp2 = 8 / bead_dict['ionization_energy'] * (bead_dict['charge'] * bead_dict['dipole']**2 * rm**2 +
                                                         bead_dict['charge'] * bead_dict['quadrupole']**2 / 5)
            partial_dict[key] = -4 * bead_dict['charge'] * rm**2 / bead_dict['ionization_energy'] + (tmp1 - tmp2) / (
                2 * np.sqrt(b - c))
        elif key == "dipole":
            tmp1 = 4 / bead_dict['ionization_energy']**2 * (
                8 / 3 * bead_dict['charge']**2 * rm**2 * bead_dict['dipole'] + 16 / 9 * bead_dict['dipole']**3 +
                8 / 5 * bead_dict['dipole'] * bead_dict['quadrupole']**2 / rm**2)
            tmp2 = 8 / bead_dict['ionization_energy'] * (
                bead_dict['charge'] * bead_dict['dipole']**2 * rm**2 + 4 / 3 * bead_dict['dipole']**3 +
                3 / 5 * bead_dict['dipole'] * bead_dict['quadrupole']**2 / rm**2)
            partial_dict[key] = -8 / 3 * bead_dict['dipole'] / bead_dict['ionization_energy'] + (tmp1 - tmp2) / (
                2 * np.sqrt(b - c))
        elif key == "quadrupole":
            tmp1 = 4 / bead_dict['ionization_energy']**2 * (12 / 5 * bead_dict['charge']**2 * bead_dict['quadrupole'] +
                                                            8 / 5 * bead_dict['dipole']**2 * bead_dict['quadrupole'] /
                                                            rm**2 + 36 / 25 * bead_dict['quadrupole']**3 / rm**4)
            tmp2 = 4 / bead_dict['ionization_energy'] * (2 / 5 * bead_dict['charge']**2 * bead_dict['quadrupole'] + 6 /
                                                         5 * bead_dict['dipole']**2 * bead_dict['quadrupole'] / rm**2 +
                                                         12 / 5 * bead_dict['quadrupole']**3 / rm**4)
            partial_dict[key] = -12 / 5 * bead_dict['quadrupole'] / bead_dict['ionization_energy'] / rm**2 + (
                tmp1 - tmp2) / (2 * np.sqrt(b - c))

    for key in partial_dict:
        if key != "charge":
            tmp = float_dimensions(partial_dict[key], key, temperature, dimensions=False)
        else:
            tmp = partial_dict[key]
        partial_dict[key] = float_dimensions(tmp, "polarizability", temperature)

    return partial_dict


def partial_energy_parameter(beadA,
                             beadB,
                             temperature=None,
                             shape_factor_scale=False,
                             sigma0=None,
                             lower_bound="rmin"):
    r"""
    Calculate partial derivative with respect to multipole moments.
    
    Parameters
    ----------
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) [K] Energy parameter scaled by Boltzmann constant
        - sigma (float) [Angstroms] Size parameter
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) [Angstroms^3] This quantity is used as a free parameter in mixing rule
        - charge (float) [-] Charge of bead fragment in elementary charges
        - dipole (float) [Debye] Dipole moment of bead fragment
        - quadrupole (float) [Debye*Angstroms] Quadrupole moment of bead fragment
        - ionization_energy (float) [kcal/mol] Ionization energy of bead fragment

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) [K] Energy parameter scaled by Boltzmann constant
        - sigma (float) [Angstroms] Size parameter
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) [Angstroms^3] This quantity is used as a free parameter in mixing rule
        - charge (float) [-] Charge of bead fragment in elementary charges
        - dipole (float) [Debye] Dipole moment of bead fragment
        - quadrupole (float) [Debye*Angstroms] Quadrupole moment of bead fragment
        - ionization_energy (float) [kcal/mol] Ionization energy of bead fragment

    temperature : float, Optional, default=298
        Temperature of the system.
    sigma0 : float, Optional, default=None
        In angstroms, this lower bound of the integral dictates where the lower bound of the definite integral is
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    lower_bound : str, Optional, default='rmin'
        Lower bound of distance array. Used only when sigma0 is None. Can be one of:

        - rmin: the position of the potential well
        - sigma: the size parameter
    
    Returns
    -------
    partial_dict : dict
        Partial derivative with respect to multipole moments
    """

    if temperature is None:
        temperature = 298
        logger.info("Using default temperature of 298 K")

    tmp = {"0": beadA.copy(), "1": beadB.copy()}
    bead_dict = dict_dimensions(tmp, temperature, dimensions=False)

    beadAB = mixed_parameters(bead_dict["0"], bead_dict["1"])
    if sigma0 is None:
        if lower_bound == "rmin":
            rm = mie_potential_minimum(beadAB)
        elif lower_bound == "sigma":
            rm = beadAB["sigma"]
    else:
        rm = sigma0

    for key1 in bead_dict:
        if "polarizability" not in bead_dict[key1]:
            r = calc_distance_array(bead_dict[key1])
            pol_tmp = solve_polarizability_integral(r[0], bead_dict[key1], shape_factor_scale=shape_factor_scale)
            if np.isnan(pol_tmp):
                raise ValueError(
                    "Error: Bead {} cannot fit suitable polarizability. No value will allow the integrated multipole moment to match the integrated Mie potential"
                    .format(bead))
            bead_dict[key1]["polarizability"] = pol_tmp

    tmp = prefactor(beadAB["lambdar"],
                    beadAB["lambdaa"]) / (beadAB["lambdaa"] - 3) * beadAB["sigma"]**beadAB["lambdaa"] / rm**(beadAB["lambdaa"] - 3)
    if shape_factor_scale:
        tmp = tmp * beadA["Sk"] * beadB["Sk"]

    partial_dict = {"0": {}, "1": {}}
    for i in [0, 1]:
        key1 = str(1 * i)
        key2 = str(1 - i)

        for key in bead_dict[key1]:
            if key == "ionization_energy":
                I = bead_dict[key2]['ionization_energy']**2 / (bead_dict[key1]['ionization_energy'] +
                                                               bead_dict[key2]['ionization_energy'])**2
                partial_dict[key1][
                    key] = bead_dict[key1]['polarizability'] * bead_dict[key2]['polarizability'] / rm**3 / 2 / tmp
            elif key == "charge":
                tmp1 = bead_dict[key1]['charge'] / rm * (bead_dict[key2]['polarizability'] +
                                                         bead_dict[key2]['dipole']**2)
                tmp2 = bead_dict[key1]['charge'] * bead_dict[key2]['quadrupole']**2 / rm**3 / 10
                partial_dict[key1][key] = (tmp1 + tmp2) / tmp
            elif key == "dipole":
                tmp1 = bead_dict[key2]['charge']**2 * bead_dict[key1]['dipole'] / rm
                tmp2 = 2 / 3 * bead_dict[key1]['dipole'] / rm**3 * (bead_dict[key2]['dipole']**2 +
                                                                    bead_dict[key2]['polarizability'])
                tmp3 = 3 / 5 / rm**5 * bead_dict[key1]['dipole'] * bead_dict[key2]['quadrupole']**2
                partial_dict[key1][key] = (tmp1 + tmp2 + tmp3) / tmp
            elif key == "quadrupole":
                tmp1 = bead_dict[key2]['charge']**2 * bead_dict[key1]['quadrupole'] / rm**3 / 5
                tmp2 = 3 / 5 * bead_dict[key1]['quadrupole'] / rm**5 * (bead_dict[key2]['dipole']**2 +
                                                                        bead_dict[key2]['polarizability'])
                tmp3 = 6 / 5 / rm**7 * bead_dict[key1]['quadrupole'] * bead_dict[key2]['quadrupole']**2
                partial_dict[key1][key] = (tmp1 + tmp2 + tmp3) / tmp
            elif key == "polarizability":
                I = bead_dict[key1]['ionization_energy'] * bead_dict[key2]['ionization_energy'] / (
                    bead_dict[key1]['ionization_energy'] + bead_dict[key2]['ionization_energy'])
                tmp1 = bead_dict[key2]['charge']**2 / rm / 2
                tmp2 = 1 / 3 / rm**3 * (bead_dict[key2]['dipole']**2 + 3 / 2 * bead_dict[key2]['polarizability'] * I)
                tmp3 = 3 / 10 / rm**5 * bead_dict[key2]['quadrupole']**2
                partial_dict[key1][key] = (tmp1 + tmp2 + tmp3) / tmp

        for key in partial_dict[key1]:
            if key != "charge":
                tmp1 = float_dimensions(partial_dict[key1][key], key, temperature, dimensions=False)
            else:
                tmp1 = partial_dict[key1][key]
            partial_dict[key1][key] = float_dimensions(tmp1, "epsilon", temperature)

    return partial_dict


def multipole_integral(sigma0, beadA, beadB, multipole_terms=None):
    r"""
    Calculate the integral of the multipole potential from a given minimum to infinity.

    Parameters
    ----------
    sigma0 : float
        This lower bound of the integral dictates where we expect to start matching the multipole attractive term with that of Mie potential. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    multipole_terms : numpy.ndarray, Optional, default=None
        This list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, respectively. If not provided, this quantity will be calculated.

    Returns
    -------
    Cmultipole : float
        Sum of integral terms. :math:`C_{multi}'=C_{multi}/(3k_{B}T)`
    multipole_int_terms : numpy.ndarray
        This list of terms corresponds to the terms involved in calculation of the energy parameter, epsilon. These terms sum to equal epsilon.

    """

    if multipole_terms is None:
        multipole_terms = calc_cross_multipole_terms(beadA, beadB)

    if np.size(multipole_terms) == 4:
        integral = -4 * np.pi * np.array([sigma0**(-1), sigma0**(-3) / 3, sigma0**(-5) / 5, sigma0**(-7) / 7])
    elif np.size(multipole_terms) == 9:
        integral = -4 * np.pi * np.array([
            sigma0**(-1), sigma0**(-1), sigma0**(-3) / 3, sigma0**(-3) / 3, sigma0**(-3) / 3, sigma0**(-3) / 3,
            sigma0**(-5) / 5, sigma0**(-5) / 5, sigma0**(-7) / 7
        ])
    else:
        raise ValueError(
            "Multipole terms input should be either of length 4 or length 9 for the supported interaction types.")

    multipole_int_terms0 = integral * multipole_terms
    Cmultipole = np.sum(multipole_int_terms0)

    return Cmultipole, multipole_int_terms0


def solve_multipole_cross_interaction_integral(sigma0,
                                               beadA,
                                               beadB,
                                               multipole_terms=None,
                                               shape_factor_scale=False,
                                               beadAB=None):
    r"""
    Calculation of nondimensionalized cross-interaction potential from multipole moments.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    sigma0 : float
        This lower bound of the integral dictates where we expect to start matching the multipole attractive term with that of Mie potential. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    beadA : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    beadB : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    multipole_terms : numpy.ndarray, Optional, default=None
        This list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, respectively. If not provided, this quantity will be calculated.
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    beadAB : dict
        Dictionary of mixed Mie parameters for beadA and beadB.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor
    
    Returns
    -------
    epsilon : float
        Cross interaction parameter from analytical solution of extended mixing rules. Array is equal in length to "r". :math:`\epsilon'=\epsilon/(3k_{B}T)`
    multipole_int_terms : numpy.ndarray
        This list of terms corresponds to the terms involved in calculation of the energy parameter, epsilon. Adding these terms together produces the attractive term of the Mie potential, from which the energy parameter can be derived.
    """

    if beadAB is None:
        beadAB = mixed_parameters(beadA, beadB)

    eps_tmp = beadAB["epsilon"]

    Cmultipole, multipole_int_terms0 = multipole_integral(sigma0, beadA, beadB, multipole_terms=multipole_terms)

    eps_min = eps_tmp / 20
    eps_max = eps_tmp * 2

    epsilon = spo.brentq(_obj_energy_parameter_from_integral,
                         eps_min,
                         eps_max,
                         args=(beadA, beadB, beadAB, Cmultipole, sigma0, shape_factor_scale),
                         xtol=1e-12)

    # __ Remove these lines so that we would have an accurate representation of the contributions without the Mie terms
    # __ Add these lines back in to be able to add the multipole terms to equal the energy parameter
    #sigmaij  = beadAB["sigma"]
    #lambdaa = beadAB["lambdaa"]
    #lambdar = beadAB["lambdar"]
    #Cmie = (sigma/sigmaij)**lambdaa * (lambdaa - 3) / prefactor(lambdar,lambdaa)
    #if shape_factor_scale:
    #    Cmie = Cmie/beadA["Sk"]/beadB["Sk"]
    #multipole_int_terms = Cmie*multipole_int_terms0
    multipole_int_terms = multipole_int_terms0

    return epsilon, multipole_int_terms


def _obj_energy_parameter_from_integral(eps0, beadA, beadB, beadAB, Cintegral, sigma0, shape_factor_scale):
    r"""
    
    Parameters
    ----------
    epsilon : float
        Guess in nondimensionalized energy parameter in [kcal/mol], math:`\epsilon'=\epsilon/(3k_{B}T)`
    bead1 : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    bead2 : dict
        Dictionary of multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    beadAB : dict
        Dictionary of mixed Mie parameters for bead1 and bead2.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    Cintegral : float
        This sum of the multipole integrals is set equal to the attractive term of the integrated Mie potential to determine the energy parameter.
    sigma0 : float
        Nondimensionalized value of the lower bound of the integral
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj

    Returns
    -------
    obj_value : float
        Difference between multipole term and Mie potential term integral
    """

    Cint = mie_integral(sigma0, beadAB)

    if shape_factor_scale:
        Cint = Cint * beadA["Sk"] * beadB["Sk"]

    return eps0 * Cint / beadAB["epsilon"] - Cintegral


def mie_integral(sigma0, beadAB):
    r"""
    Calculate the integral of the attractive term in the Mie potential from the given minimum value to infinity.
    
    Parameters
    ----------
    sigma0 : float
        Minimum value for definite integral
    beadAB : dict
        Dictionary of mixed Mie parameters for bead1 and bead2.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    Returns
    -------
    Cintegral : float
        Value of the definite Mie integral from sigma0 to infinity
    """

    integral = -4 * np.pi * beadAB["epsilon"] * prefactor(
        beadAB["lambdar"],
        beadAB["lambdaa"]) * beadAB["sigma"]**beadAB["lambdaa"] / sigma0**(beadAB["lambdaa"] - 3) / (beadAB["lambdaa"] - 3)

    return integral


def fit_multipole_cross_interaction_parameter(beadA,
                                              beadB,
                                              distance_dict={},
                                              distance_array=None,
                                              fit_attractive_exp=False,
                                              shape_factor_scale=False,
                                              temperature=None):
    r"""
    Calculation of nondimensionalized cross-interaction parameter for the Mie potential.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    beadA : dict
        Dictionary of Mie and multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    beadB : dict
        Dictionary of Mie and multipole parameters for bead_B.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    fit_attractive_exp : bool, Optional, default: False
        If true, the attractive exponential will be fit along with the energy parameter
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    temperature : float, Optional, default=None
        Temperature at which to evaluate cross interaction parameters, needed to add dimensions to error messages if this step fails.

    Returns
    -------
    output_dict : dict
        Dictionary of fit epsilon and lambdar, 
    """

    # Set-up Mie parameters
    beadAB = mixed_parameters(beadA, beadB)
    Cmie = prefactor(beadAB["lambdar"], beadAB["lambdaa"])
    if shape_factor_scale:
        if "Sk" not in beadA:
            beadA["Sk"] = 1.0
        if "Sk" not in beadB:
            beadB["Sk"] = 1.0

    multipole_terms = calc_cross_multipole_terms(beadA, beadB)

    # From curve fit
    if distance_array is None:
        r = calc_distance_array(beadAB, **distance_dict)
    else:
        r = distance_array
    w_multipole, potential_terms = calc_cross_multipole_potential(r, multipole_terms, total_only=False)

    # ___________ VDW parameter mixing _______________
    params, var_matrix = spo.curve_fit(lambda x, K, lambdaa: log_mie_attractive(
        r, beadA, beadB, lambda_a=lambdaa, Kprefactor=K, shape_factor_scale=shape_factor_scale),
                                       r,
                                       np.log(-w_multipole),
                                       p0=[beadAB["epsilon"] * Cmie, beadAB["lambdaa"]],
                                       bounds=(0.0, np.inf))
    K = params[0]
    lambdaa_fit = params[1]
    eps_fit = calc_epsilonij_from_lambda_aij(lambdaa_fit, beadA, beadB)
    if K / eps_fit < 1.01:
        raise ValueError(
            "A suitable repulsive exponent cannot be calculated using the following cross interaction parameters:\n    epsilon: {}, lambdaa: {}, Cmie: {} < 1.0\n    Check self-interaction parameters above. A common cause could be poorly fit polarizability because a partial charge was assigned to an bead where it's Mie potential is fit to expect dipole to be the highest order."
            .format(float_dimensions(eps_fit, "epsilon", temperature), lambdaa_fit, K / eps_fit))
    else:
        try:
            lambdar_fit = spo.brentq(lambda x: K / eps_fit - prefactor(x, lambdaa_fit), lambdaa_fit * 1.01, 1e+4, xtol=1e-12)
        except:
            raise ValueError("This shouldn't happen, check given parameters.")

    # Save output
    output_dict = {}
    output_dict["lambdaa_fit"] = lambdaa_fit
    output_dict["epsilon_fit"] = eps_fit
    output_dict["lambdar_fit"] = lambdar_fit
    output_dict["epsilon_saft"] = beadAB["epsilon"] * np.sqrt(
        beadA["sigma"]**3 * beadB["sigma"]**3) / beadAB["sigma"]**3
    output_dict["kij_saft"] = 1 - output_dict["epsilon_saft"] / beadAB["epsilon"]
    output_dict["kij_fit"] = 1 - output_dict["epsilon_fit"] / beadAB["epsilon"]

    output_dict["lambdaa_variance"] = var_matrix[0][0]
    output_dict["K_variance"] = var_matrix[1][1]

    # From analytical solution
    beadC = {"epsilon": eps_fit, "lambdar": lambdar_fit, "lambdaa": lambdaa_fit, "sigma": beadAB["sigma"]}
    _, terms = solve_multipole_cross_interaction_integral(r[0],
                                                          beadA,
                                                          beadB,
                                                          multipole_terms=multipole_terms,
                                                          shape_factor_scale=shape_factor_scale,
                                                          beadAB=beadC)
    output_dict["terms_int"] = terms

    return output_dict


def log_mie_attractive(r, bead1, bead2, lambda_a=None, Kprefactor=None, epsilon=None, shape_factor_scale=False):
    r"""
    Calculate the log of the attractive term of the Mie potential. This linearizes the curve for the fitting process

    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    bead1 : dict
        Dictionary of multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    bead2 : dict
        Dictionary of multipole parameters for bead_B. If provided, the mixed energy parameter is fit.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - Sk (float) Shape factor

    epsilon : float, Optional, default=None
        The energy parameter for the Mie potential, if not specified the mixing rule from Lafitte 2013 is used
    lambda_a : float, Optional, default=None
        The cross interaction attractive exponent, if not specified the mixing rule from Lafitte 2013 is used
    Kprefactor : float, Optional, default=None
        Total prefactor of Mie potential equal to the energy parameters times the Mie prefactor, C. If not specified, the value using the mixing rules from Lafitte 2013 is used.
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj

    Returns
    -------
    log_potential : numpy.ndarray
        The potential array for the given value of epsilon
    """

    beadAB = mixed_parameters(bead1, bead2)
    sigma = beadAB["sigma"]
    lambda_r = beadAB["lambdar"]

    if epsilon is not None and lambda_a is not None:
        # Assume lambdar follows normal mixing rules
        Kprefactor = epsilon * prefactor(lambda_r, lambda_a)
    elif epsilon is not None and Kprefactor is not None:
        raise ValueError("Specifying 'epsilon' and 'Kprefactor' is redundant.")
    elif epsilon is not None:
        # Assume both exponents follow normal mixing rules
        lambda_a = beadAB["lambdaa"]
        Kprefactor = epsilon * prefactor(lambda_r, lambda_a)
    elif lambda_a is not None and Kprefactor is None:
        # Assume lambdar follows normal mixing rules, epsilon can be derived from 1 fluid mixing rule
        epsilon = calc_epsilonij_from_lambda_aij(lambda_a, bead1, bead2)
        Kprefactor = epsilon * prefactor(lambda_r, lambda_a)
    elif lambda_a is None and Kprefactor is not None:
        # Assume lambdaa follows normal mixing rules
        lambda_a = beadAB["lambdaa"]

    if shape_factor_scale:
        Kprefactor = Kprefactor * bead1["Sk"] * bead2["Sk"]

    return np.log(Kprefactor) + lambda_a * np.log(sigma / r)


def calc_self_mie_from_multipole(
    bead_dict,
    mie_vdw=None,
    temperature=298,
    lambda_r=12,
    distance_dict={},
    distance_array=None,
    shape_factor_scale=False,
):
    r"""
    Calculation of self-interaction parameters for the Mie potential from multipole moments.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    bead_dict : dict
        Dictionary of Mie and multipole parameters for bead_A.

        - epsilon (float) Nondimensionalized energy parameter, :math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalized size parameter, :math:`\sigma'=\sigma (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) Nondimensionalized polarizability of bead. :math:`\alpha'=\alpha (4 \pi \epsilon_{0})^{2} 3k_{B}T  e^{-6}`
        - charge (float) Nondimensionalized charge of bead. :math:`q'=q/e`
        - dipole (float) Nondimensionalized dipole of bead. :math:`\mu'=\mu (4 \pi \epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalized quadrupole of bead. :math:`Q'=Q (4 \pi \epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalized ionization_energy of bead. :math:`I'=I/(3k_{B}T)`

    mie_vdw : float, Optional, default=None
        This nondimensionalized attractive parameter for the Mie potential is related not only to the Mie exponents but also to the triple and critical temperatures of a substance. It can be used to specify the repulsive exponent, otherwise a value of 12 is assumed
    lambda_r : float, Optional, default=12
        Assumed repulsive exponent. This quantity can be changed later as long as the energy parameter is scaled accordingly.
    temperature : float, Optional, default=298
        The temperature of the system in Kelvin
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    distance_dict : dict, Optional, default={}
        Optional keywords for creating r array used for calculation or fitting 

    Returns
    -------
    cross_dict : dict
        Dictionary with energy parameter and exponents for Mie cross interaction between the given beads.
    """

    tmp_dict = {"tmp": bead_dict.copy()}
    tmp_dict = dict_dimensions(tmp_dict, temperature, dimensions=False)
    bead_dict_new = tmp_dict["tmp"]

    if shape_factor_scale:
        if "Sk" not in bead_dict_new:
            bead_dict_new["Sk"] = 1.0

    multipole_terms = calc_cross_multipole_terms(bead_dict_new, bead_dict_new)
    if distance_array is None:
        r = calc_distance_array(bead_dict_new, **distance_dict)
    else:
        r = distance_array
    w_multipole, potential_terms = calc_cross_multipole_potential(r, multipole_terms, total_only=False)

    Cmie = prefactor(bead_dict_new["lambdar"], bead_dict_new["lambdaa"])
    params, var_matrix = spo.curve_fit(lambda x, K, lambdaa: log_mie_attractive(
        r, bead_dict_new, bead_dict_new, lambda_a=lambdaa, Kprefactor=K, shape_factor_scale=shape_factor_scale),
                                       r,
                                       np.log(-w_multipole),
                                       p0=[bead_dict_new["epsilon"] * Cmie, bead_dict_new["lambdaa"]],
                                       bounds=(0.0, np.inf))
    K = params[0]
    bead_dict_new["lambdaa"] = params[1]
    if mie_vdw is not None:
        logger.info("Overwrite given lambdar with Mie potential relationship to vdW like parameter.")
        bead_dict_new["lambdar"] = calc_lambdarij_from_lambda_aij(bead_dict_new["lambdaa"], mie_vdw)
    else:
        bead_dict_new["lambdar"] = lambda_r

    if shape_factor_scale:
        bead_dict_new["epsilon"] = K / prefactor(bead_dict_new["lambdar"], bead_dict_new["lambdaa"]) / bead_dict_new["Sk"]**2
    else:
        bead_dict_new["epsilon"] = K / prefactor(bead_dict_new["lambdar"], bead_dict_new["lambdaa"])

    tmp_dict = {"tmp": bead_dict_new}
    tmp_dict = dict_dimensions(tmp_dict, temperature, dimensions=False)

    return tmp_dict["tmp"]


def extended_mixing_rules_fitting(bead_library, temperature, shape_factor_scale=False, distance_dict={}):
    r"""
    Calculate and output the cross-interaction parameters for the provided dictionary of beads utilizing the Mie potential.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    bead_library : dict
        Dictionary of dictionaries with Mie and multipole parameters for each bead in the desired system.

        - epsilon (float) [K] Energy parameter scaled by Boltzmann constant
        - sigma (float) [Angstroms] Size parameter
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) [Angstroms^3] This quantity is used as a free parameter in mixing rule
        - charge (float) [-] Charge of bead fragment in elementary charges
        - dipole (float) [Debye] Dipole moment of bead fragment
        - quadrupole (float) [Debye*Angstroms] Quadrupole moment of bead fragment
        - ionization_energy (float) [kcal/mol] Ionization energy of bead fragment

    temperature : float
        The temperature of the system
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    distance_dict : dict, Optional, default={}
        Optional keywords for creating r array used for calculation or fitting 

    Returns
    -------
    cross_dict : dict
        Dictionary with "epsilon" value for cross interaction for the given beads.
    summary : list[list]
        For each pair contains list with two bead names, cross interaction and binary interaction parameters for the SAFT mixing rules, the cross interaction and binary interaction parameters with exponents for multipole curve fit, the polarizabilities for the two beads, and the integral terms for each multipole contribution from the lower limit to infinite.
    """

    bead_library_new = dict_dimensions(bead_library.copy(), temperature, dimensions=False)

    # calculate polarizability
    for bead in bead_library_new.keys():
        r = calc_distance_array(bead_library_new[bead], **distance_dict)
        pol_tmp, _ = fit_polarizability(r, bead_library_new[bead], shape_factor_scale=shape_factor_scale)
        if np.isnan(pol_tmp):
            raise ValueError(
                "Error: Bead {} cannot fit suitable polarizability. Attractive exponent is most likely not suitable given the bead partial charges."
            )
        bead_library_new[bead]["polarizability"] = pol_tmp

    # Calculate cross interaction file
    dict_cross = {}
    summary = []
    beads = list(bead_library_new.keys())
    for i, bead1 in enumerate(beads):
        if len(beads[i + 1:]) > 0:
            dict_cross[bead1] = {}
            for bead2 in beads[i + 1:]:
                if np.any(
                        np.isnan(
                            [bead_library_new[bead1]["polarizability"], bead_library_new[bead2]["polarizability"]])):
                    raise ValueError("Error: polarizabilities of {} and {}: {}, {}".format(
                        bead1, bead2, bead_library_new[bead1]["polarizability"],
                        bead_library_new[bead2]["polarizability"]))

                cross_out = fit_multipole_cross_interaction_parameter(bead_library_new[bead1],
                                                                      bead_library_new[bead2],
                                                                      distance_dict=distance_dict,
                                                                      shape_factor_scale=shape_factor_scale,
                                                                      temperature=temperature)

                pol_i = float_dimensions(bead_library_new[bead1]["polarizability"], "polarizability", temperature)
                pol_j = float_dimensions(bead_library_new[bead2]["polarizability"], "polarizability", temperature)
                epsilon_saft = float_dimensions(cross_out["epsilon_saft"], "epsilon", temperature)
                epsilon_fit = float_dimensions(cross_out["epsilon_fit"], "epsilon", temperature)

                dict_cross[bead1][bead2] = {
                    "epsilon": cross_out["epsilon_fit"],
                    "lambdar": cross_out["lambdar_fit"],
                    "lambdaa": cross_out["lambdaa_fit"]
                }
                summary.append([
                    bead1, bead2, epsilon_saft, cross_out["kij_saft"], epsilon_fit, cross_out["kij_fit"],
                    cross_out["lambdar_fit"], cross_out["lambdaa_fit"], pol_i, pol_j
                ] + cross_out["terms_int"].tolist())

    dict_cross = dict_dimensions(dict_cross.copy(), temperature)

    return dict_cross, summary


def extended_mixing_rules_analytical(bead_library, temperature, shape_factor_scale=False, distance_dict={}):
    r"""
    Calculate and output the cross-interaction energy parameter for the provided dictionary of beads utilizing the Mie potential, using the Analytical (i.e. integral) method

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    bead_library : dict
        Dictionary of dictionaries with Mie and multipole parameters for each bead in the desired system.

        - epsilon (float) [K] Energy parameter scaled by Boltzmann constant
        - sigma (float) [Angstroms] Size parameter
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) [Angstroms^3] This quantity is used as a free parameter in mixing rule
        - charge (float) [-] Charge of bead fragment in elementary charges
        - dipole (float) [Debye] Dipole moment of bead fragment
        - quadrupole (float) [Debye*Angstroms] Quadrupole moment of bead fragment
        - ionization_energy (float) [kcal/mol] Ionization energy of bead fragment

    temperature : float
        The temperature of the system
    shape_factor_scale : bool, Optional, default: False
        Scale energy parameter based on shape factor epsilon*Si*Sj
    distance_dict : dict, Optional, default={}
        Optional keywords for creating r array used for calculation or fitting 

    Returns
    -------
    cross_dict : dict
        Dictionary with "epsilon" value for cross interaction for the given beads.
    summary : list[list]
        For each pair contains list with two bead names, cross interaction and binary interaction parameters for the SAFT mixing rules, the cross interaction and binary interaction parameters with exponents for multipole analytical calculation (exponents use saft mixing), the polarizability for the two beads, the potential coefficients for the multipole moment, and finally the integral terms.
    """

    bead_library_new = dict_dimensions(bead_library.copy(), temperature, dimensions=False)
    # calculate polarizability
    for bead in bead_library_new.keys():
        r = calc_distance_array(bead_library_new[bead], **distance_dict)
        pol_tmp = solve_polarizability_integral(r[0], bead_library_new[bead], shape_factor_scale=shape_factor_scale)
        if np.isnan(pol_tmp):
            raise ValueError(
                "Error: Bead {} cannot fit suitable polarizability. No value will allow the integrated multipole moment to match the integrated Mie potential"
                .format(bead))
        bead_library_new[bead]["polarizability"] = pol_tmp

    # Calculate cross interaction file
    dict_cross = {}
    summary = []
    beads = list(bead_library_new.keys())
    for i, bead1 in enumerate(beads):
        beadA = bead_library_new[bead1]
        if len(beads[i + 1:]) > 0:
            dict_cross[bead1] = {}
            for bead2 in beads[i + 1:]:
                beadB = bead_library_new[bead2]
                if np.any(np.isnan([beadA["polarizability"], beadB["polarizability"]])):
                    raise ValueError("Error: polarizabilities of {} and {}: {}, {}".format(
                        bead1, bead2, beadA["polarizability"], beadB["polarizability"]))

                beadAB = mixed_parameters(beadA, beadB)
                r = calc_distance_array(beadAB, **distance_dict)
                epsilon_tmp, terms = solve_multipole_cross_interaction_integral(r[0],
                                                                                beadA,
                                                                                beadB,
                                                                                shape_factor_scale=shape_factor_scale)

                pol_i = float_dimensions(beadA["polarizability"], "polarizability", temperature)
                pol_j = float_dimensions(beadB["polarizability"], "polarizability", temperature)
                eps_saft_tmp = beadAB["epsilon"] * np.sqrt(beadA["sigma"]**3 * beadB["sigma"]**3) / beadAB["sigma"]**3
                epsilon_saft = float_dimensions(eps_saft_tmp, "epsilon", temperature)
                epsilon_analytical = float_dimensions(epsilon_tmp, "epsilon", temperature)
                kij_saft = 1 - eps_saft_tmp / beadAB["epsilon"]
                kij_analytical = 1 - epsilon_tmp / beadAB["epsilon"]
                summary.append([
                    bead1, bead2, epsilon_saft, kij_saft, epsilon_analytical, kij_analytical, beadAB["lambdar"],
                    beadAB["lambdaa"], pol_i, pol_j
                ] + terms.tolist())

                dict_cross[bead1][bead2] = {"epsilon": epsilon_tmp}

    dict_cross = dict_dimensions(dict_cross.copy(), temperature)

    return dict_cross, summary


def dict_dimensions(parameters, temperature, dimensions=True, conv_custom={}):
    r"""
    Obtain instructions for systems used in calculation.

    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    parameters : dict
        This dictionary of bead types contains a dictionary of parameters for each.

        - epsilon (float) Nondimensionalize energy parameter in [K], math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalize size parameter in [angstroms], :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) Nondimensionalize polarizability of bead in [angstroms^3]. math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume
        - charge (float) Nondimensionalize charge of bead in [e]. :math:`q'=q/e`
        - dipole (float) Nondimensionalize dipole of bead in [Debye]. :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalize quadrupole of bead in [Debye*angstrom]. :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalize ionization_energy of bead in [kcal/mol]. :math:`I'=I/(3k_{B}T)`

    temperature : float
        The temperature of the system
    dimensions : bool, Optional, default: True
        If true, will add SI-units to multipole parameters, if False, will nondimensionalize. 
    conv_custom : dict, Optional, default: {}
        This dictionary may have the same parameter names used for the beads and overwrite default values.

    Returns
    -------
    new_parameters : dict
        This dictionary of bead types contains a dictionary of parameters for each.
    """

    # Nondimensionalize Parameters
    C_l = 1e+10  # [Ang/m]
    C_D = 3.33564e-20  # [C*Ang/Debye]
    C_e = 6.9477e-21  # [J / kcal/mol]
    C_eV = 1.602176565e-19  # [J/eV]
    e0 = 8.854187817e-12 * C_e / C_l  # [C^2/(J*m)] to [C^2*mol/(kcal*Ang)]
    kb = 1.38064852e-23 / C_e  # [J/K] to [kcal/(mol*K)] Boltzmann constant

    perm = (4 * np.pi * e0)**2  # [C^2*mol/(kcal*Ang)]^2
    K = 3 * kb * temperature  # [kcal/mol]

    conv = {"epsilon": 1/(3*temperature), \
            "ionization_energy": 1/K,
            "sigma": np.sqrt(perm)*K/C_eV**2, \
            "dipole": C_D*np.sqrt(perm)*K/C_eV**3, \
            "quadrupole": C_D*perm*K**2/C_eV**5, \
            "charge":1, \
            "polarizability": 4*np.pi*e0*perm*K**3/C_eV**6}
    #            "polarizability": perm*K**3/C_eV**6} Using the polarizability is in large units

    for key, value in conv_custom.items():
        conv[key] = value

    new_parameters = {}
    for k1, v1 in parameters.items():
        new_parameters[k1] = {}
        for k2, v2 in v1.items():
            if type(v2) == dict:
                new_parameters[k1][k2] = {}
                for k3, v3 in v2.items():
                    if k3 in conv:
                        if dimensions:
                            new_parameters[k1][k2][k3] = v3 / conv[k3]
                        else:
                            new_parameters[k1][k2][k3] = v3 * conv[k3]
                    else:
                        new_parameters[k1][k2][k3] = v3
            else:

                if k2 in conv:
                    if dimensions:
                        new_parameters[k1][k2] = v2 / conv[k2]
                    else:
                        new_parameters[k1][k2] = v2 * conv[k2]
                else:
                    new_parameters[k1][k2] = v2

    return new_parameters


def float_dimensions(parameter, parameter_type, temperature, dimensions=True, conv_custom={}):
    r"""
    Obtain instructions for systems used in calculation.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    parameter : float
        Value of parameter to be converted.
    parameter_type : str
        Parameter name, can be:
    
        - epsilon (float) Nondimensionalize energy parameter in [K], math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Nondimensionalize size parameter in [angstroms], :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - polarizability (float) Nondimensionalize polarizability of bead in [angstroms^3]. math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume
        - charge (float) Nondimensionalize charge of bead in [e]. :math:`q'=q/e`
        - dipole (float) Nondimensionalize dipole of bead in [Debye]. :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Nondimensionalize quadrupole of bead in [Debye*angstrom]. :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Nondimensionalize ionization_energy of bead in [kcal/mol]. :math:`I'=I/(3k_{B}T)`
    
    temperature : float
        The temperature of the system
    dimensions : bool, Optional, default: True
        If true, will add SI-units to multipole parameters, if False, will nondimensionalize.
    conv_custom : dict, Optional, default: {}
        This dictionary may have the same parameter names used for the beads and overwrite default values.
    
    Returns
    -------
    new_parameter : float
        Converted parameter
    """

    # Nondimensionalize Parameters
    C_l = 1e+10  # [Ang/m]
    C_D = 3.33564e-20  # [C*Ang/Debye]
    C_e = 6.9477e-21  # [J / kcal/mol]
    C_eV = 1.602176565e-19  # [J/eV]
    e0 = 8.854187817e-12 * C_e / C_l  # [C^2/(J*m)] to [C^2*mol/(kcal*Ang)]
    kb = 1.38064852e-23 / C_e  # [J/K] to [kcal/(mol*K)] Boltzmann constant

    perm = (4 * np.pi * e0)**2  # [C^2*mol/(kcal*Ang)]^2
    K = 3 * kb * temperature  # [kcal/mol]

    conv = {"epsilon": 1/(3*temperature), \
            "ionization_energy": 1/K,
            "sigma": np.sqrt(perm)*K/C_eV**2, \
            "dipole": C_D*np.sqrt(perm)*K/C_eV**3, \
            "quadrupole": C_D*perm*K**2/C_eV**5, \
            "charge":1, \
            "polarizability": 4*np.pi*e0*perm*K**3/C_eV**6}

    for key, value in conv_custom.items():
        conv[key] = value

    if parameter_type in conv:
        if dimensions:
            new_parameter = parameter / conv[parameter_type]
        else:
            new_parameter = parameter * conv[parameter_type]
    else:
        raise KeyError("Parameter, {}, is not supported. Must be one of: {}".format(parameter_type, list(conv.keys())))

    return new_parameter


if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print("This is an imported module!")
