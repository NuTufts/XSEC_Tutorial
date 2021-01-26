# XSEC_Tutorial
A Tutorial for using RooUnfold to Extract a Cross Section.

The goal of this repository is to provide all the tools necessary to try to use RooUnfold to perform unfolding and then extract a cross section. Example data, monte carlo simulated signal, and background are all included. The example shown performs a cross section extraction from the DL 1m1p Selection in MicroBooNE. Make sure that you have sourced root in order to use this tutorial. This has been tested on Root6 built with Python3.5.2 

The python code tutorials should be well commented, and the process broken down. In order to get started, `source first_setup.sh` which will clone https://gitlab.cern.ch/RooUnfold/RooUnfold into the Tutorial Repository, then move the python scripts into the RooUnfold Directory so that they can use the RooUnfold tools. 

Then `cd RooUnfold` and play around with the jupyter notebooks.
`Tutorial_RooUnfold_Data.ipynb`    is a notebook designed to show how to extract a cross section from data.


