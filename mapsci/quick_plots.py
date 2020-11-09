
import numpy as np
import mapsci.multipole_mie_combining_rules as mr

def plot_multipole_potential(r, potential, potential_terms=None, show=True):
    r"""
    Plot multipole potential and if provided, the contribution of each multipole interaction.
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. Reported in :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads based on multipole moments. Array is equal in length to "r". Reported in nondimensionalized :math:`\phi'=\phi/(3k_{B}T)`
    potential_terms : numpy.ndarray
        This can be either a list of terms corresponds to the coefficients for r to the order of -4, -6, -8, and -10, or a list of nine terms terms corresponding to the coefficients the various multipole interactions. Calculated from :func:`~mapsci.multipole_mie_combining_rules.calc_cross_multipole_terms`
    show : bool, Optional, default=True
        Dictate whether plt.show() should be executed within this function
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

def plot_potential(r, potential, plot_opts={}, show=True):
    r"""
    Plot given potential
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.

    Parameters
    ----------
    r : numpy.ndarray
        Array (or float) of nondimensionalized distance between two beads. Reported in angstroms or :math:`r'=r (4 \pi \epsilon_{0}) 3k_{B}T e^{-2}`
    potential : numpy.ndarray
        Array of nondimensionalized potential between beads based on multipole moments. Array is equal in length to "r". Reported in units reduced by the Boltzmann constant, [K] or nondimensionalized as :math:`\phi'=\phi/(3k_{B}T)`
    plot_opts : dict, Optional, default={}
        Keyword arguments for matplotlib.pyplot.plot
    show : bool, Optional, default=True
        Dictate whether plt.show() should be executed within this function
    """

    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:
        plt.xlabel("Dimensionless Distance")
        plt.ylabel("Dimensionless Potential")

        plt.plot(r, potential, **plot_opts)

        if show:
            plt.legend(loc="best")
            plt.tight_layout()
            plt.show()

def plot_abs_dev_mie_multipole_potentials(bead_dict0, beadAB={}, distance_opts={}, temperature=None, nondimensional=False, plot_opts={}, axs=None, title=None, ylabel="default", xlabel="default"):
    r"""
    Plot absolute deviation between Mie and Multipole potentials
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.

    Parameters
    ----------
    bead_dict0 : dict
        Dictionary of Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K], or nondimensionalized as math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Size parameter in [angstroms], or nondimensionalized as :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e], or nondimensionalized as :math:`q'=q/e`
        - dipole (float) Dipole of bead in [Debye], or nondimensionalized as :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom], or nondimensionalized as :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol], or nondimensionalized as :math:`I'=I/(3k_{B}T)`
        - polarizability (float) Polarizability of bead in [angstroms^3] or nondimensionalized with math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume

    beadAB : dict, Optional, default={}
        Dictionary of cross-interaction parameters for Mie potential.
        
        - epsilon (float) Energy parameter in [K], or nondimensionalized as math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Size parameter in [angstroms], or nondimensionalized as :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent

    distance_opts : dict, Optional, default={}
        Dictionary of keyword arguments for :func:`~mapsci.multipole_mie_combining_rules.calc_distance_array`
    temperature : float, Optional, default=None
        Temperature in [K] for adding and removing dimensions, if the parameters are nondimensionalized, this value isn't used.
    nondimensional : bool, Optional, default=False
        Indicates whether the given bead library has been nondimensionalized by :func:`~mapsci.multipole_mie_combining_rules.dict_dimensions`
    plot_opts : dict, Optional, default={}
        Keyword arguments for matplotlib.pyplot.plot
    axs : obj, Optional, default=None
        Subplot instance, if none, matplotlib.pyplot.plot is used 
    title : str, Optional, default=None
        Title of plot or subplot (if axs object is provided)
    ylabel : str, Optional, default="$(V_{Mie}-V_{Multipole})/(3k_{B}T)$" or in kcal/mol
        Label for y-axis, if None, the label is removed
    xlabel : str, Optional, default="r [$\AA$]"/"r $\it{e}^2/(4\pi\epsilon_0 3k_BT)$"
        Label for x-axis, if None, the label is removed. The default value is determined by `nondimensional`
    """

    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:

        if not nondimensional:
            if temperature is None:
                logger.error("Temperature should be included with 'nondimensional' is False")
            bead_dict = mr.dict_dimensions(bead_dict0.copy(), temperature, dimensions=False)
            if len(beadAB) > 0:
                beadAB0 = mr.dict_dimensions(beadAB.copy(), temperature, dimensions=False)
        else:
            bead_dict = bead_dict0.copy()

        tmp = [True if type(value)==dict else False for _,value in bead_dict.items()]
        if np.all(tmp):
            keys = list(bead_dict.keys())
            flag = True
        elif np.any(tmp):
            raise ValueError("Dictionary should be either a single beads parameters, or a dictionary of dictionaries containing the parameters of several beads.")
        else:
            flag = False 

        if flag:
            bead12 = mr.fit_multipole_cross_interaction_parameter(bead_dict[keys[0]], bead_dict[keys[1]], distance_opts=distance_opts, nondimensional=True)
            if len(beadAB0) != 0:
                bead12.update(beadAB0)

            r = mr.calc_distance_array(bead12, **distance_opts)

            w_Mie = mr.calc_mie_attractive_potential(r, bead12)
            multipole_terms = mr.calc_cross_multipole_terms(bead_dict[keys[0]], bead_dict[keys[1]], nondimensional=True)
            w_multipole, potential_terms = mr.calc_cross_multipole_potential(r,multipole_terms, total_only=False)

        else:
            r = mr.calc_distance_array(bead_dict, **distance_opts)

            w_Mie = mr.calc_mie_attractive_potential(r, bead_dict)
            multipole_terms = mr.calc_cross_multipole_terms( bead_dict, bead_dict, nondimensional=True)
            w_multipole, potential_terms = mr.calc_cross_multipole_potential(r,multipole_terms, total_only=False)

        y = w_Mie-w_multipole

        if not nondimensional:
            r = mr.float_dimensions(r, "sigma", temperature)
            y = mr.float_dimensions(y, "ionization_energy", temperature)

        if not nondimensional:
            if xlabel == "default":
                xlabel = r"r [$\AA$]"
            if ylabel == "default":
                ylabel="$V_{Mie}-V_{Multipole}$ [kcal/mol]"
        else:
            if xlabel == "default":
                xlabel = r"r $\it{e}^2/(4\pi\epsilon_0 3k_BT)$"
            if ylabel == "default":
                ylabel="$(V_{Mie}-V_{Multipole})/(3k_{B}T)$"

        if axs != None:

            if type(axs) == list:
                raise ValueError("One subplot object should be given")

            axs.plot(r, y, **plot_opts)
            if ylabel != None:
                axs.set_ylabel(ylabel)
            if xlabel != None:
                axs.set_xlabel(xlabel)
        else:
            plt.plot(r, y, **plot_opts)
            if ylabel != None:
                plt.ylabel(ylabel)
            if xlabel != None:
                plt.xlabel(xlabel)
     
        if title != None:
            if axs != None:
                axs.set_title(title)
            else:
                plt.title(title)

def plot_self_potential_absolute_deviation(bead_library, temperature=None, nondimensional=False, distance_opts={}, polarizability_opts={}, plot_opts={}, axs=None):
    r"""
    Plot absolute deviation between Mie and Multipole potentials for a set of beads
    
    Parameters
    ----------
    bead_library : dict
        Dictionary of beads and associated dictionaries of their Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K], or nondimensionalized as math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Size parameter in [angstroms], or nondimensionalized as :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e], or nondimensionalized as :math:`q'=q/e`
        - dipole (float) Dipole of bead in [Debye], or nondimensionalized as :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom], or nondimensionalized as :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol], or nondimensionalized as :math:`I'=I/(3k_{B}T)`
        - polarizability (float) Polarizability of bead in [angstroms^3] or nondimensionalized with math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume

    distance_opts : dict, Optional, default={}
        Dictionary of keyword arguments for :func:`~mapsci.multipole_mie_combining_rules.calc_distance_array`
    temperature : float, Optional, default=None
        Temperature in [K] for adding and removing dimensions, if the parameters are nondimensionalized, this value isn't used.
    nondimensional : bool, Optional, default=False
        Indicates whether the given bead library has been nondimensionalized by :func:`~mapsci.multipole_mie_combining_rules.dict_dimensions`
    polarizability_opts : dict, Optional, default={}
        Options used in :func:`~mapsci.multipole_mie_combining_rules.fit_polarizability` or :func:`~mapsci.multipole_mie_combining_rules.calc_polarizability`. Used if polarizability isn't provided for all beads.
    plot_opts : dict, Optional, default={}
        Keyword arguments for matplotlib.pyplot.plot
    axs : obj, Optional, default=None
        Subplot instance, if none, matplotlib.pyplot.plot is used 
    """

    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:

        bead_library_new = bead_library.copy()
    
        if not np.all([True if "polarizability" in x else False for _,x in bead_library_new.items()]):
            bead_library_new = mr.calc_polarizability(bead_library_new, distance_opts=distance_opts, nondimensional=nondimensional, temperature=temperature, polarizability_opts=polarizability_opts)
    
        if np.any(axs == None):
            _, axs = plt.subplots(1,len(bead_library))
    
        for i, (bead, bead_dict) in enumerate(bead_library_new.items()):
    
            title = "Absolute Deviation for {}".format(bead)
            if i != 0:
                ylabel = None
            else:
                ylabel = "default"
    
            plot_abs_dev_mie_multipole_potentials(bead_dict, distance_opts=distance_opts, nondimensional=nondimensional, temperature=temperature, plot_opts=plot_opts, axs=axs[i], title=title, ylabel=ylabel)

def plot_cross_potential_absolute_deviation(beadA, beadB, temperature=None, nondimensional=False, distance_opts={}, polarizability_opts={}, **kwargs):
    r"""
    Plot absolute deviation between Mie and Multipole potentials for a set of beads
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.

    Parameters
    ----------
    beadA : dict
        Dictionary of a bead's Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K], or nondimensionalized as math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Size parameter in [angstroms], or nondimensionalized as :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e], or nondimensionalized as :math:`q'=q/e`
        - dipole (float) Dipole of bead in [Debye], or nondimensionalized as :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom], or nondimensionalized as :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol], or nondimensionalized as :math:`I'=I/(3k_{B}T)`
        - polarizability (float) Polarizability of bead in [angstroms^3] or nondimensionalized with math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume

    beadB : dict
        Dictionary of a bead's Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K], or nondimensionalized as math:`\epsilon'=\epsilon/(3k_{B}T)`
        - sigma (float) Size parameter in [angstroms], or nondimensionalized as :math:`\sigma'=\sigma (4 \pi epsilon_{0}) 3k_{B}T e^{-2}`
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e], or nondimensionalized as :math:`q'=q/e`
        - dipole (float) Dipole of bead in [Debye], or nondimensionalized as :math:`\mu'=\mu (4 \pi epsilon_{0}) 3k_{B}T e^{-3}`
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom], or nondimensionalized as :math:`Q'=Q (4 \pi epsilon_{0})^{2} (3k_{B}T)^{2} e^{-5}`
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol], or nondimensionalized as :math:`I'=I/(3k_{B}T)`
        - polarizability (float) Polarizability of bead in [angstroms^3] or nondimensionalized with math:`\alpha'=\alpha (4 \pi \epsilon_{0}) 3k_{B}T  e^{-6}`, where the dimensionalized version is the polarizability volume

    distance_opts : dict, Optional, default={}
        Dictionary of keyword arguments for :func:`~mapsci.multipole_mie_combining_rules.calc_distance_array`
    temperature : float, Optional, default=None
        Temperature in [K] for adding and removing dimensions, if the parameters are nondimensionalized, this value isn't used.
    nondimensional : bool, Optional, default=False
        Indicates whether the given bead library has been nondimensionalized by :func:`~mapsci.multipole_mie_combining_rules.dict_dimensions`
    polarizability_opts : dict, Optional, default={}
        Options used in :func:`~mapsci.multipole_mie_combining_rules.fit_polarizability` or :func:`~mapsci.multipole_mie_combining_rules.calc_polarizability`. Used if polarizability isn't provided for all beads.
    kwargs
        Other keyword arguments to be passed to :func:`~mapsci.quick_plots.plot_abs_dev_mie_multipole_potentials`
    """
    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:

        if "polarizability" not in beadA:
            bead1 = mr.calc_polarizability(beadA.copy(), distance_opts=distance_opts, nondimensional=nondimensional, temperature=temperature, polarizability_opts=polarizability_opts)
        else: 
            bead1 = beadA.copy()

        if "polarizability" not in beadA:
            bead2 = mr.calc_polarizability(beadB.copy(), distance_opts=distance_opts, nondimensional=nondimensional, temperature=temperature, polarizability_opts=polarizability_opts)
        else:
            bead2 = beadA.copy()

        bead_library_new = {"bead1": bead1, "bead2": bead2}

        plot_abs_dev_mie_multipole_potentials(bead_library_new, distance_opts=distance_opts, nondimensional=nondimensional, temperature=temperature, **kwargs)
            
def plot_mie_multipole_integral_difference(beadA, beadB, temperature, polarizability_opts={}, lower_bounds=["rmin","sigma"], max_factors=[1.5,1.75,2,2.25,2.5,3,4], savefig=True, filename="integral_difference.pdf", show=True):
    r"""
    Plot absolute deviation between Mie and Multipole potentials for a set of beads
    
    Nondimensional parameters are scaled using the following physical constants: vacuum permittivity, :math:`\epsilon_{0}`, Boltzmann constant, :math:`k_{B}`, and elementary charge, :math:`e`.
    
    Parameters
    ----------
    beadA : dict
        Dictionary of a bead's Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K]
        - sigma (float) Size parameter in [angstroms]
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e]
        - dipole (float) Dipole of bead in [Debye]
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom]
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol]
        - polarizability (float) Polarizability of bead in [angstroms^3]

    beadB : dict
        Dictionary of a bead's Mie and multipole parameters. Those parameters may be:
        
        - epsilon (float) Energy parameter in [K]
        - sigma (float) Size parameter in [angstroms]
        - lambdar (float) Repulsive exponent
        - lambdaa (float) Attractive exponent
        - charge (float) Charge of bead in [e]
        - dipole (float) Dipole of bead in [Debye]
        - quadrupole (float) Quadrupole of bead in [Debye*angstrom]
        - ionization_energy (float) Ionization_energy of bead in [kcal/mol]
        - polarizability (float) Polarizability of bead in [angstroms^3]

    temperature : float
        Temperature in [K] for adding and removing dimensions
    polarizability_opts : dict, Optional, default={}
        Options used in :func:`~mapsci.multipole_mie_combining_rules.fit_polarizability` or :func:`~mapsci.multipole_mie_combining_rules.calc_polarizability`. Used if polarizability isn't provided for all beads.
    lower_bounds : list, Optional, default=["rmin","sigma"]
        Dictates the number of subplots, this represents the method of determining the lower bound for curve fitting in :func:`~mapsci.multipole_mie_combining_rules.calc_distance_array`
    max_factors : list, Optional, default=[1.5,1.75,2,2.25,2.5,3,4]
        Dictates the number of points in the plot line, this represents the multiple of the lower bound that defines the upper bound in :func:`~mapsci.multipole_mie_combining_rules.calc_distance_array`
    savefig : bool, Optional, default=True
        Dictate whether plt.savefig() should be executed within this function
    filename : str, Optional, default="integral_difference.pdf"
        If 'savefig' is True, save the figure to this filename.
    show : bool, Optional, default=True
        Dictate whether plt.show() should be executed within this function    
    """

    try:
        import matplotlib.pyplot as plt
        plot_fit = True
    except:
        logger.error("Package matplotlib is not available")
        plot_fit = False

    if plot_fit:

        labels = {"rmin": "$r_{min}$", "sigma": "$\sigma_{ij}$"}

        bead1 = beadA.copy()
        bead2 = beadB.copy()
        bead_library = {"bead1": bead1, "bead2": bead2}

        var_array = [[],[]]
        for i, lb in enumerate(lower_bounds):
            for factor in max_factors:
        
                distance_opts = {"max_factor": factor, "lower_bound": lb}
                tmp_library = mr.calc_polarizability(bead_library, temperature=temperature, distance_opts=distance_opts, polarizability_opts=polarizability_opts)

                beadAB = mr.fit_multipole_cross_interaction_parameter(tmp_library["bead1"], tmp_library["bead2"], distance_opts=distance_opts, temperature=temperature)
                Cmulti, _ = mr.multipole_integral(tmp_library["bead1"], tmp_library["bead2"],  lower_bound=lb, temperature=temperature)
                CMie = mr.mie_integral(beadAB, lower_bound=lb)
        
                var_array[i].append([Cmulti, CMie])

        var_array = [np.transpose(np.array(var_array[0])), np.transpose(np.array(var_array[1]))]

        fig, axs = plt.subplots(1,len(lower_bounds))
        for i, lb in enumerate(lower_bounds):
            axs[i].plot(max_factors,var_array[i][0],label="Multipole")
            axs[i].plot(max_factors,var_array[i][1],label="Mie")
            ax2 = axs[i].twinx()
            ax2.tick_params(axis='y', labelcolor="r")
            ax2.plot(max_factors, var_array[i][0]-var_array[i][1], "r")
            if i == 1:
                ax2.set_ylabel('Difference')
            elif i == 0:
                axs[i].legend(loc="best")
        
        axs[0].set_title("{} Integral to Infinity".format(labels[lower_bounds[0]]))
        axs[1].set_title("{} Integral to Infinity".format(labels[lower_bounds[1]]))
        axs[0].set_xlabel("Max Factor")
        axs[1].set_xlabel("Max Factor")
        plt.tight_layout()

        if savefig:
            plt.savefig(filename,dpi=600)

        if show:
            plt.show()
            plt.close()

