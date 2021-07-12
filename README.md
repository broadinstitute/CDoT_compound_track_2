Track Compounds Run
===============================

[![Build Status](https://travis-ci.com/bfulroth/track_compounds_run.svg?branch=master)](https://travis-ci.com/bfulroth/track_compounds_run)

Project to be use to track where compounds are made and when they were tested.

Requirements
------------
__If using Mac OS 10.15 and greater:__

*If you haven't installed `xcode`, `homebrew`, or `pipenv` please follow steps 1-4.*

1. Install `xcode` command line tools<br/>
command line: `xcode-select --install`

2. Install `hombrew`<br/>
command line: ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

3. Install Python > 3.6 using Miniconda
command line' `brew cask install miniconda`
   
4. Clone the master branch of this repo locally.

5. Create a conda virtual environment by invoking the following command: `conda env create`.

6. Activate the conda virtual environment before running the app: `conda activate CMPD_TRACKING`

Usage
-----

__Note:__ This app requires a Google API Key as well as a Broad Internal network connection.

__Note:__ This app requires an encrypted database password in a .env file.  The encripted password can be found on 
the Broad internal server at the path below.  Copy this file into this repo.

__/Iron/tdts_users/SPR to ADLP Python Script Overview__

__Invoke CLI:__ `python -m make_updated_tracking_sheet`

__Options:__ `python -m make_updated_tracking_sheet -f` will enable reading from a .csv file rather than from
 Google Sheets directly.  Google sheets will not be updated but an Exel file containig compounds without data will still be save to the destop..

Google Sheet tab "__Compounds Received but not Tested__" will be updated.

An Excel File with updated dates that the compounds were run, a pivot table, and the above Google Sheet tab will be saved to
 the desktop.
 



 
License
-------
This project is licensed under the terms of the [MIT License](/LICENSE)
