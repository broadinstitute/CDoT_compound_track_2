Track Compounds Run
===============================

[![Build Status](https://travis-ci.com/bfulroth/track_compounds_run.svg?branch=master)](https://travis-ci.com/bfulroth/track_compounds_run)

Project to be use to track where compounds are made and when they were tested.

Requirements
------------
__If using Mac OS 10.15 and greater:__

*If you haven't installed `xcode`, `homebrew`, or `pipenv` please follow steps 1-3.*

1. Install `xcode` command line tools<br/>
command line: `xcode-select --install`

2. Install `hombrew`<br/>
command line: ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

3. Install `pipenv`<br/>
command line: `brew install pipenv`

Usage
-----

__Note:__ This app requires a Google API Key as well as a Broad Internal network connection.

__Create and activate a virtual environment using Pipenv__ command line: `pipenv install --dev`<br/>

__Invoke CLI:__ `python -m make_updated_tracking_sheet`

__Options:__ `python -m make_updated_tracking_sheet -f` will enable reading from a .csv file rather than directly from
 Google Sheets directly.  Google sheets will not be updated.

Google Sheet tab "__Compounds Received but not Tested__" will be updated.

An Excel File with updated dates the compounds were run, a pivot table, and the above Google Sheet tab will be saved to
 the desktop.
 



 
License
-------
This project is licensed under the terms of the [MIT License](/LICENSE)
