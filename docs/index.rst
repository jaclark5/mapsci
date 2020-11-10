.. mapsci documentation master file, created by
   sphinx-quickstart on Thu Mar 15 13:55:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MAPSCI's documentation!
=========================================================

MAPSCI (Multipole Approach of Predicting and Scaling Cross Interactions) is an importable package used to estimate temperature-dependent cross-interaction parameters for the Mie potential using multipole moments. This is useful for the SAFT-𝛾-Mie equation of state, as well as Molecular Dynamics and Monte Carlo simulation methods.

This package can be a "black box" in thermodynamics calculations achieved with `DESPASITO <https://github.com/jaclark5/despasito>`_ or as an imported package for scripting. A user will most often use the following higher-level functions:

- :func:`~mapsci.multipole_mie_combining_rules.calc_polarizability`
- :func:`~mapsci.multipole_mie_combining_rules.calc_self_mie_from_multipole`
- :func:`~mapsci.multipole_mie_combining_rules.extended_mixing_rules_fitting`
- :func:`~mapsci.multipole_mie_combining_rules.extended_mixing_rules_analytical`

These and other functions are defined in the API documentation. There, the quick_plots module contains optional tools to visualize the theory that is package contains. Lastly, the default behavior of this package is to not share calculation details with logging, although this capability can be enabled with the :func:`~mapsci.initiate_logger` utility.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
