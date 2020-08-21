MAPSCI
==============================
[//]: # (Badges)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Travis Build Status](https://travis-ci.com/jaclark5/MAPSCI.svg?branch=master)](https://travis-ci.com/jaclark5/MAPSCI)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/m9p1qg5y1aq0swd6/branch/master?svg=true)](https://ci.appveyor.com/project/jaclark5/MAPSCI/branch/master)
[![codecov](https://codecov.io/gh/jaclark5/MAPSCI/branch/master/graph/badge.svg)](https://codecov.io/gh/jaclark5/MAPSCI/branch/master)
[![Documentation Status](https://readthedocs.org/projects/mapsci/badge/?version=latest)](https://mapsci.readthedocs.io)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jaclark5/mapsci.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jaclark5/mapsci/context:python)


MAPSCI: Multipole Approach of Predicting and Scaling Cross Interactions

**WARNING!** This package is not ready for distribution.

What is this?
-------------
MAPSCI is an importable package that can be used to estimate cross-interaction parameters for the Mie potential using multipole moments. This is useful for the SAFT-𝛾-Mie equation of state, as well as Molecular Dynamics and Monte Carlo simulation methods.

How do I use it?
----------------
Once installed, you can:
 * Import the package and use it in a python script. We have provided helpful functions to organize your data. Be aware that the parameters are temperature dependent.
 * This package can be used as a plug-in for our equation of state package, [DESPASITO](https://github.com/jaclark5/despasito). You won't need to worry about temperature dependence in this case, it'll be taken care of internally.
Check out our [documentation](https://mapsci.readthedocs.io) for more information.

Installation
------------
**NOTE:** Coming soon to pip

Download the master branch from our github page as a zip file, or clone it with git via ``git clone https://github.com/jaclark5/mapsci`` in your working directory. Install MAPSCI locally from the working directory with ``python setup.py install --user``.

### Copyright

Copyright (c) 2020, Jennifer A Clark


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.
