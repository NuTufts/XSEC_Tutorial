#!/bin/bash

git clone https://:@gitlab.cern.ch:8443/RooUnfold/RooUnfold.git
cp *.ipynb RooUnfold/
cp *.root RooUnfold/
cp *.py RooUnfold/
cd RooUnfold/
make
