# muse-reduction
A script used to reduce the data from the MUSE instrument on the VLT.
This script was written as part of my 2016 Summer Scholarship at MQU/AAO

To run this script call:

`python muse_reduction_script.py [PATH TO DATA DIRECTORY]`

Or if this file was renamed call:

`python [NAME HERE].py [PATH TO DATA DIRECTORY]`

The calibration data can be in another folder. This is suggested. 
The script will ask for this directory first.
There is an automatic mode, however I suggest doing it manually to have more control over the script.

Currently there is no option to use darks as part of the reduction.

There are 4 parts to this code:

PART 0: DEFINE VARIABLES AND FILE NAMES          

PART 1: IDENTIFY THE CALIBRATION DATA           

PART 2: SORTING THE DATA FILES                  

PART 3: CREATING THE SET OF FRAMES (SOF)        

PART 4: DATA REDUCTION                          
