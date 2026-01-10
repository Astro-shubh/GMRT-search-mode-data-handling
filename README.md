# Process batch of GMRT search mode data
Convert uGMRT raw data files to sigproc-filterbank format and generate folded archive files. Total intensity, both in 16-bit and 8-bit data formats, is supported at present. Working on extracting total intensity from full Stokes GMRT data and converting it to filterbank.

Installation
============

The package has two parts: one part in Python to handle the filesystem, inputs, and outputs. The second part is a modified version of ugmrt2fil that can handle both 8-bit and 16-bit raw GMRT data.
1. `Processing_modules:` This contains Python modules needed by the main processGMRT.py code. These modules require standard python packages installed. One needs to change `path_ugmrt2fil` in the `Processing_modules/processGMRT_global.py` to the current `CPP_utilities` directory and path_par to a folder containing parameter files. Also, change the `data_path` in `processGMRT.py` to the folder containing GMRT raw and header files. The folding part requires `dspsr` installed.
2. `CPP_utilities:` This folder contains modified ugmrt2fil codes and should be installed using `make` within `CPP_utilities` directory before use.

Usage
======

`$ python processGMRT.py`
