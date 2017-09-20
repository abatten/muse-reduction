# MUSE DATA REDUCTION SCRIPT - ADAM BATTEN 2016

# To run this script call:
# 'python muse_reduction_script.py [PATH TO DATA DIRECTORY]'
# Or if this file was renamed call:
# 'python [NAME HERE].py [PATH TO DATA DIRECTORY]'

# The calibration data can be in another folder. This is suggested. 
# The script will ask for this directory first.
# There is an automatic mode, however I suggest doing it manually to have more control over the script.

# Currently there is no option to use darks as part of the reduction.
# 

# There are 4 parts to this code:
# PART 0: DEFINE VARIABLES AND FILE NAMES         LN  ~24 - 149 
# PART 1: IDENTIFY THE CALIBRATION DATA           LN  ~149 - 529
# PART 2: SORTING THE DATA FILES                  LN  ~529 - 650
# PART 3: CREATING THE SET OF FRAMES (SOF)        LN  ~650 - 871
# PART 4: DATA REDUCTION                          LN  ~871 - END

import pyfits,glob,sys
from subprocess import call

# STEP 0: DEFINE VARIABLES AND FILE NAMES
# ---------------------------------------

# These are the variables that specify whether or not certian recipies should be performed.
auto_mode = False
perform_bias = 'n'
perform_dark = 'n'
perform_flat = 'n'
perform_wavecal = 'n'
perform_lsf = 'n'
perform_twilight = 'n'
perform_scibasic_object = 'n'
perform_scibasic_std = 'n'
perform_standard = 'n'
perform_scibasic_sky = 'n'
perform_create_sky = 'n'
perform_scipost = 'n'

# The first argument the user specifies is the path to the data directory
try:
	science_data_directory = sys.argv[1]
except:
	print 'No path given.'
	sys.exit(0)

# Check to see if a path is specified. If so, use that path.
if len(sys.argv) == 1:
        data_files = glob.glob('/MUSE.*fits.fz') # List the MUSE data files in directory. Calib data not included.
        all_fits = glob.glob('/*.fits')

elif len(sys.argv) == 2:
        data_files = glob.glob(str(science_data_directory + '/MUSE.*fits.fz')) # List the MUSE data files in directory. Calib data not included.
        all_fits = glob.glob(str(science_data_directory + '/*.fits'))
else:
        print('Too many arguments!')
        sys.exit(0)

# Ask the user for the directory where the calibration data is located
calib_data_directory = raw_input('Please specify the path to the directory containing the calibration files:')

static_calibration_data = glob.glob(str(calib_data_directory + '/M.MUSE*.fits')) # List the static calibration files in the directory.

# Ask user if they want to run in auto mode. There will still be some prompts though. It is suggested to say No.
user_auto_mode = raw_input('Run script in auto mode? (Not Recomended)(y/n): ')
if user_auto_mode in ('y', 'yes', 'Yes', 'Y'):
	print('---Running in Automatic Mode---')
	auto_mode = True
	perform_bias = 'y'
	perform_dark = 'n'
	perform_flat = 'y'
	perform_wavecal = 'y'
	perform_lsf = 'y'
	perform_twilight = 'y'
	perform_scibasic_object = 'y'
	perform_scibasic_std = 'y'
	perform_standard = 'y'
	perform_scibasic_sky = 'y'
	perform_create_sky = 'y'
	perform_scipost = 'y'

elif user_auto_mode in ('n', 'no', 'No', 'N'):
	print('')
	print('---Running in Manual Mode---')
	print('')
else:
	print('ERROR: Input not a valid response')
	sys.exit(0)

# Remove any static calibration data from the all fits list.
for i in range(len(static_calibration_data)):
	if static_calibration_data[i] in all_fits:
		all_fits.remove(static_calibration_data[i])


# Prints out each line of a list line by line
# This was used during testing to ensure that the lists contain the correct file names.
def print_lines(input_list):
	for i in range(len(input_list)):
     		print input_list[i]

# Define empty list for each of the OJBECT types.
bias_list =[]
flat_lamp_list = []
flat_sky_list  = []
wave_list = []
std_list = []
object_list= []
dark_list = []
illum_list = []
object_sky_list = []

# Define variables to be used for input files
	# These files must be supplied.
LINE_CATALOG = ''
GEOMETRY_TABLE = ''
VIGNETTING_MASK = ''
BADPIX_TABLE = ''
EXTINCT_TABLE = ''
STD_FLUX_TALE = ''
SKY_LINES = ''
ASTROMETRY_WCS = ''
ASTROMETRY_REFERENCE = ''
FILTER_LIST = ''

	# Default names for files that can be created. 
LSF_PROFILE = 'LSF_PROFILE.fits'
MASTER_BIAS = 'MASTER_BIAS.fits'
MASTER_FLAT = 'MASTER_FLAT.fits'
TRACE_TABLE = 'TRACE_TABLE.fits'
WAVECAL_TABLE = 'WAVECAL_TABLE.fits'
TWILIGHT_CUBE = 'TWILIGHT_CUBE.fits'
STD_RESPONSE = 'STD_RESPONSE_0001.fits'
STD_TELLURIC = 'STD_TELLURIC_0001.fits'
MASTER_DARK = 'MASTER_DARK.fits'

# Variables that indicated whether or not specific files already exist in directory.
# Default is that none of the files exist.
MASTER_BIAS_EXIST = False
MASTER_FLAT_EXIST = False
TRACE_TABLE_EXIST = False
WAVECAL_TABLE_EXIST = False
TWILIGHT_CUBE_EXIST = False
STD_RESPONSE_EXIST = False
STD_TELLURIC_EXIST = False
LSF_PROFILE_EXIST = False
MASTER_DARK_EXIST = False
BADPIX_TABLE_EXIST = False
SKY_CONTINUUM_EXIST = False

# STEP 1: IDENTIFY THE CALIBRATION FILES
# --------------------------------------

# Look and categorise all the Static Calibration Data and give appropriate variable names.
print(' ')
print('STEP 1:')
print('---Searching for Static Calibration Data---')
print(' ')

num_calib_files = 0 # Variable to keep track of the number of calib files sorted
for i in range(len(static_calibration_data)):
        temp=pyfits.open(static_calibration_data[i])
        try:
                hierarch = temp[0].header['HIERARCH ESO PRO CATG'] # Unique header keyword for each file type (PRO CATG = Product Category)
		if 'LINE_CATALOG' in hierarch:
			LINE_CATALOG = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/') # spl is short for 'split'.
			print 'Found: ' +  spl[-1], '    LINE_CATALOG'
			num_calib_files += 1

		elif 'VIGNETTING_MASK' in hierarch:
			VIGNETTING_MASK = static_calibration_data[i]
			spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    VIGNETTING_MASK'
			num_calib_files += 1

                elif 'BADPIX_TABLE' in hierarch:
			BADPIX_TABLE = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    BADPIX_TABLE'
			BADPIX_TABLE_EXIST = True
                        num_calib_files += 1

		elif 'GEOMETRY_TABLE' in hierarch:
			GEOMETRY_TABLE = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    GEOMETRY_TABLE'
                        num_calib_files += 1

                elif 'EXTINCT_TABLE' in hierarch:
                        EXTINCT_TABLE = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    EXTINCT_TABLE'
                        num_calib_files += 1

		elif 'ASTROMETRY_WCS' in hierarch:
			ASTROMETRY_WCS = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    ASTROMETRY_WCS'
                        num_calib_files += 1

		elif 'ASTROMETRY_REFERENCE' in hierarch:
			ASTROMETRY_REFERENCE = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    ASTROMETRY_REFERENCE'
                        num_calib_files += 1

                elif 'STD_FLUX_TABLE' in hierarch:
                        STD_FLUX_TABLE = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    STD_FLUX_TABLE'
                        num_calib_files += 1

		elif 'SKY_LINES' in hierarch:
			SKY_LINES = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    SKY_LINES'
			num_calib_files += 1

		elif 'FILTER_LIST' in hierarch:
			FILTER_LIST = static_calibration_data[i]
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    FILTER_LIST'
                        num_calib_files += 1

		elif 'LSF_PROFILE' in hierarch:
			LSF_PROFILE = static_calibration_data[i]
			LSF_PROFILE_EXIST = True
			perform_lsf = 'n'
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    LSF_PROFILE'
                        num_calib_files += 1

		elif 'MASTER_BIAS' in hierarch:
			MASTER_BIAS = static_calibration_data[i]
			MASTER_BIAS_EXIST = True
			perform_bias = 'n'
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    MASTER_BIAS'
			num_calib_files += 1

                elif 'MASTER_FLAT' in hierarch:
                        MASTER_FLAT = static_calibration_data[i]
                        MASTER_FLAT_EXIST = True
                        perform_flat = 'n'
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    MASTER_FLAT'
                        num_calib_files += 1

                elif 'MASTER_DARK' in hierarch:
                        MASTER_DARK = static_calibration_data[i]
                        MASTER_DARK_EXIST = True
                        perform_dark = 'n'
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    MASTER_DARK'
                        num_calib_files += 1

                elif 'TRACE_TABLE' in hierarch:
                        TRACE_TABLE = static_calibration_data[i]
                        TRACE_TABLE_EXIST = True
                        perform_flat = 'n'
                        spl = static_calibration_data[i].split('/')
                        print 'Found: ' + spl[-1], '    TRACE_TABLE'
                        num_calib_files += 1

		elif 'WAVECAL_TABLE' in hierarch:
			WAVECAL_TABLE = static_calibration_data[i]
			WAVECAL_TABLE_EXIST = True
			perform_wavecal = 'n'
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    WAVECAL_TABLE'
			num_calib_files += 1

		elif 'TWILIGHT_CUBE' in hierarch:
			TWILIGHT_CUBE = static_calibration_data[i]
			TWILIGHT_CUBE_EXIST = True
			perform_twilight = 'n'
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    TWILIGHT_CUBE'
			num_calib_files += 1

		elif 'STD_RESPONSE' in hierarch:
			STD_RESPONSE = static_calibration_data[i]
			STD_RESPONSE_EXIST = True
			perform_standard = 'n'
                        spl = static_calibration_data[i].split('/')
			print 'Found: ' + spl[-1], '    STD_RESPONSE'
			num_calib_files += 1

		elif 'STD_TELLURIC' in hierarch:
			STD_TELLURIC = static_calibration_data[i]
			STD_TELLURIC_EXIST = True
			perform_standard = 'n'
			print 'Found: ' + spl[-1], '    STD_TELLURIC'
			num_calib_files += 1

                else:
			print static_calibration_data[i], 'Data Type Not Found' 
        except:
                print static_calibration_data[i],'Exception when trying to find calibration data'
		sys.exit(0)

# Check to make sure all the file types were found
print ''
print('Process found ' + str(num_calib_files) + ' calibration files')
if num_calib_files == len(static_calibration_data):
	print ''
	print('All calibration files were assigned')
else:
	print ''
	print('At least 1 calibration file\'s type could not be found')

print ''
print '---Finished finding calibration data---'
print ''

# Looks to see if there are any already made files in the directory
print('---Checking files in current directory---')
for i in range(len(all_fits)):
        temp=pyfits.open(all_fits[i])
        try:
                hierarch = temp[0].header['HIERARCH ESO PRO CATG'] # Unique header keyword for each file type
                if 'MASTER_BIAS' in hierarch:
			if MASTER_BIAS_EXIST == False: # If MASTER_BIAS doesn't exist yet, use this file as the MASTER_BIAS
                        	MASTER_BIAS = all_fits[i]
				spl = all_fits[i].split('/')
                        	print 'Found: ' + spl[-1], '    '+ hierarch
				MASTER_BIAS_EXIST = True
			elif MASTER_BIAS_EXIST == True: # If a MASTER_BIAS file was already found. Ask which should be used.
				print('')
				print('Found: A second MASTER_BIAS')
				print('To use ' + MASTER_BIAS + ' (old) type 1.') 
				print('To use ' + all_fits[i] + ' (new) type 2.')
				number = raw_input('Type number here: ')
                                if number == '1':
                                        MASTER_BIAS = all_fits[i]
                                        spl = MASTER_BIAS.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = MASTER_BIAS.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
				else:	
					print('Not an acceptable response')
					sys.exit(0)

                elif 'MASTER_FLAT' in hierarch:
                        if MASTER_FLAT_EXIST == False:
                                MASTER_FLAT = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                MASTER_FLAT_EXIST = True
                        elif MASTER_FLAT_EXIST == True:
                                print('Found: A second MASTER_FLAT was found.')
                                print('To use ' + MASTER_FLAT + ' (old) type 1.')
				print('To use ' + all_fits[i] + ' (new) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        MASTER_FLAT = all_fits[i]
                                        spl = MASTER_FLAT.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = MASTER_FLAT.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)


                elif 'TRACE_TABLE' in hierarch:
                        if TRACE_TABLE_EXIST == False:
                                TRACE_TABLE = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                TRACE_TABLE_EXIST = True
                        elif TRACE_TABLE_EXIST == True:
                                print('Found: A second TRACE_TABLE was found.')
                                print('To use ' + TRACE_TABLE + ' (old) type 1.')
				print('To use ' + all_fits[i] + ' (new) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        TRACE_TABLE = all_fits[i]
                                        spl = TRACE_TABLE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = TRACE_TABLE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)


                elif 'WAVECAL_TABLE' in hierarch:
                        if WAVECAL_TABLE_EXIST == False:
                                WAVECAL_TABLE = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                WAVECAL_TABLE_EXIST = True
                        elif WAVECAL_TABLE_EXIST == True:
                                print('Found: A second WAVECAL_TABLE was found.')
                                print('To use ' + WAVECAL_TABLE + ' (old) type 1.')
				print('To use ' + all_fits[i] + ' (new) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        WAVECAL_TABLE = all_fits[i]
                                        spl = WAVECAL_TABLE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = WAVECAL_TABLE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)


                elif 'LSF_PROFILE' in hierarch:
                        if LSF_PROFILE_EXIST == False:
                                LSF_PROFILE = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                LSF_PROFILE_EXIST = True
                        elif LSF_PROFILE_EXIST == True:
				print('')
                                print('Found: A second LSF_PROFILE')
                                print('To use ' + all_fits[i] + ' (new) type 1.')
				print('To use ' + LSF_PROFILE + ' (old) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        LSF_PROFILE = all_fits[i]
                                        spl = LSF_PROFILE.split('/')
					print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
				elif number == '2':
                                        spl = LSF_PROFILE.split('/')
					print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)


                elif 'TWILIGHT_CUBE' in hierarch:
                        if TWILIGHT_CUBE_EXIST == False:
                                TWILIGHT_CUBE = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                TWILIGHT_CUBE_EXIST = True
                        elif TWILIGHT_CUBE_EXIST == True:
                                print('')
                                print('Found: A second TWILIGHT_CUBE')
                                print('To use ' + all_fits[i] + ' (new) type 1.')
                                print('To use ' + TWILIGHT_CUBE + ' (old) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        TWILIGHT_CUBE = all_fits[i]
                                        spl = TWILIGHT_CUBE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = TWILIGHT_CUBE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)

                elif 'STD_RESPONSE' in hierarch:
                        if STD_RESPONSE_EXIST == False:
                                STD_RESPONSE = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                STD_RESPONSE_EXIST = True
                        elif STD_RESPONSE_EXIST == True:
                                print('')
                                print('Found: A second STD_RESPONSE')
                                print('To use ' + all_fits[i] + ' (new) type 1.')
                                print('To use ' + STD_RESPONSE + ' (old) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        STD_RESPONSE = all_fits[i]
                                        spl = STD_RESPONSE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = STD_RESPONSE.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)

                elif 'STD_TELLURIC' in hierarch:
                        if STD_TELLURIC_EXIST == False:
                                STD_TELLURIC = all_fits[i]
                                spl = all_fits[i].split('/')
                                print 'Found: ' + spl[-1], '    '+ hierarch
                                STD_TELLURIC_EXIST = True
                        elif STD_TELLURIC_EXIST == True:
                                print('')
                                print('Found: A second STD_TELLURIC')
                                print('To use ' + all_fits[i] + ' (new) type 1.')
                                print('To use ' + STD_TELLURIC + ' (old) type 2.')
                                number = raw_input('Type number here: ')
                                if number == '1':
                                        STD_TELLURIC = all_fits[i]
                                        spl = STD_TELLURIC.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                elif number == '2':
                                        spl = STD_TELLURIC.split('/')
                                        print ' '
                                        print 'Using: ' + spl[-1], '    '+ hierarch
                                else:
                                        print('Not an acceptable response')
                                        sys.exit(0)

	except:
		print(all_fits[i], 'Exception when trying to find calibration data')
		sys.exit(0)                 


print('---Finished checking files in path directory---')


# STEP 2: SORTING THE DATA FILES
# ------------------------------
print(' ')
print('STEP 2:')
print('---Sorting data---')
print(' ')
print 'Working Directory: ' + science_data_directory
print ''

# Variables to keep track of number of files sorted and the amount of each type.
num_data_files = 0 
num_bias = 0
num_flat_lamp = 0
num_flat_sky = 0
num_wave = 0
num_std = 0
num_dark = 0
num_illum = 0
num_object_sky = 0
num_object = 0

# This for loop checks the header for each data file and determines what type it is.
print 'FILE NAME |', 'OBJECT |', 'DPR TYPE'
for i in range(len(data_files)):
	temp=pyfits.open(data_files[i])
	try:
		object_header = temp[0].header['OBJECT']
		dpr_type = temp[0].header['HIERARCH ESO DPR TYPE']
		if 'BIAS' in dpr_type: # BIAS FRAME
			bias_list.append(data_files[i])
			num_data_files += 1
			num_bias += 1
			spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type

		elif 'FLAT,LAMP' == dpr_type: # LAMP FLAT FRAME
			flat_lamp_list.append(data_files[i])
                        num_data_files += 1
			num_flat_lamp += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type

                elif 'FLAT,SKY' in dpr_type: # SKY FLAT FRAME
                        flat_sky_list.append(data_files[i])
                        num_data_files += 1
			num_flat_sky += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type

                elif 'WAVE' in dpr_type: # WAVELENGTH CALIBRATION FRAME
                        wave_list.append(data_files[i])
                        num_data_files += 1
			num_wave += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type

                elif 'STD' in object_header: # STANDARD CALIBRATION FRAME
                        std_list.append(data_files[i])
                        num_data_files += 1
			num_std += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type
		
		elif 'DARK' in dpr_type: # DARK FRAME
			dark_list.append(data_files[i])
                        num_data_files += 1
			num_dark += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type
		
		elif 'FLAT,LAMP,ILLUM' == dpr_type: # ILLUMINATION FLAT FRAME
			illum_list.append(data_files[i])
                        num_data_files += 1
			num_illum += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type
		
		elif 'SKY' in dpr_type: # SKY FRAME
			object_sky_list.append(data_files[i])
                        num_data_files += 1
			num_object_sky += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type
		
		elif 'OBJECT' in dpr_type: #SCIENCE OBJECT DATA
			object_list.append(data_files[i])
			num_data_files += 1
			num_object += 1
                        spl = data_files[i].split('/')
                        print spl[-1],'    ' + object_header,'    ' +  dpr_type

		else:
			print(data_files[i], 'Could Not Sort!!!', object_header, dpr_type)
	except:
		print(data_files[i],'Doesn''t have a DPR TYPE')

print ''

# Prints out how many files of each type were found
print('Process found:')
print ''
print('- '+ str(num_bias) + ' Bias Frames')
print('- '+ str(num_dark) + ' Dark Frames')
print('- '+ str(num_flat_lamp) + ' Lamp Flat Frames')
print('- '+ str(num_flat_sky) + ' Sky Flat Frames')
print('- '+ str(num_wave) + ' Arc Frames')
print('- '+ str(num_std) + ' Standard Frames')
print('- '+ str(num_illum) + ' Illum Frames')
print('- '+ str(num_object_sky) + ' Object Sky Frames')
print('- '+ str(num_object) + ' Object Frames')	
print('A total of ' + str(num_data_files) + ' data files were found.')
if num_data_files == len(data_files):
	print ''
	print('All data files were sorted')
else:
	print ''
	print('At least 1 file was not able to be sorted')
print ''
print('---Finished Sorting Data---')
print ''


# PART 3: CREATING SET OF FRAMES (SOF)
# ------------------------------------

# Creates a text file from a given input list.
def write_list(type_list, file_name):
	name = file_name
	try:
		f = open(name, "w")
		f.write("\n".join(map(lambda x: str(x), type_list)))
		f.close()
	except:
        	print('Something went wrong! Can\'t write to the file: ' + name)
        	sys.exit(0) # quit Python


# The following are the definitions on how to construct the set of frame (sof) files. 
# Each definition also checks to ensure that the required files already exist in the directory.


# At the moment the script only uses 15 bias frames because it never finishes muse_bias if I use all of them.
def create_bias_sof():
# bias.sof is to be used for muse_bias
#	for i in range(len(bias_list)):
	for i in range(15):
		bias_list[i] = bias_list[i] + ' ' + 'BIAS'
	write_list(bias_list, 'bias.sof')
	print ''
        print('Created bias.sof')

def create_flat_sof():
# flat.sof is to be used for muse_flat
	if MASTER_BIAS_EXIST == True:
		for i in range(len(flat_lamp_list)):
			flat_lamp_list[i] = flat_lamp_list[i] + ' ' + 'FLAT'
		flat_lamp_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
		write_list(flat_lamp_list, 'flat_lamp_list.sof')
        	print ''
		print('Created flat.sof')
	elif MASTER_BIAS_EXIST == False:
		print ''
		print('ERROR: MASTER_BIAS does not exist. Can not create flat.sof')
		sys.exit(0)


# Similarly as the bias, muse_wavecal only uses 15 frames just so it will finish.
def create_wavecal_sof():
# wavecal.sof is to be used for muse_wavecal
	if MASTER_BIAS_EXIST == True and TRACE_TABLE_EXIST == True:
#		for i in range(len(wave_list)):
		for i in range(15):
			wave_list[i] = wave_list[i] + ' ' + 'ARC'
		wave_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
		wave_list.append(TRACE_TABLE + ' ' + 'TRACE_TABLE')
		wave_list.append(LINE_CATALOG + ' ' + 'LINE_CATALOG')
		write_list(wave_list, 'wavecal.sof')
        	print ''
		print('Created wavecal.sof')
	elif MASTER_BIAS_EXIST == False:
		print ''
		print('ERROR: MASTER_BIAS does not exist. Can not create wavecal.sof')
		sys.exit(0)
	elif TRACE_TABLE_EXIST == False:
		print ''
		print('ERROR: TRACE_TABLE does not exist. Can not create wavecal.sof')
		sys.exit(0)

def create_lsf_sof():
# lsf.sof is to be used for muse_lsf
	if WAVECAL_TABLE_EXIST == True and MASTER_BIAS_EXIST == True and TRACE_TABLE_EXIST == True:
		lsf_list = wave_list
		lsf_list.append(WAVECAL_TABLE + ' ' + 'WAVECAL_TABLE')
        	write_list(lsf_list, 'lsf.sof')
		print ''
		print('Created lsf.sof')
        elif MASTER_BIAS_EXIST == False:
                print ''
		print('ERROR: MASTER_BIAS does not exist. Can not create wavecal.sof')
                sys.exit(0)
        elif TRACE_TABLE_EXIST == False:
                print ''
		print('ERROR: TRACE_TABLE does not exist. Can not create wavecal.sof')
                sys.exit(0)
	elif WAVECAL_TABLE_EXIST == False:
                print ''
		print('ERROR: WAVECAL_TABLE does not exist. Can not create wavecal.sof')
		sys.exit(0)

def create_twilight_sof():
# twilight.sof is to be used for muse_twilight
	if  all([MASTER_BIAS_EXIST == True, MASTER_FLAT_EXIST == True, TRACE_TABLE_EXIST == True, WAVECAL_TABLE_EXIST == True]):
        	for i in range(len(flat_sky_list)):
                	flat_sky_list[i] = flat_sky_list[i] + ' ' + 'SKYFLAT'
        	flat_sky_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
		flat_sky_list.append(MASTER_FLAT + ' ' + 'MASTER_FLAT')
        	flat_sky_list.append(TRACE_TABLE + ' ' + 'TRACE_TABLE')
		flat_sky_list.append(VIGNETTING_MASK + ' ' + 'VIGNETTING_MASK')
        	flat_sky_list.append(GEOMETRY_TABLE + ' ' + 'GEOMETRY_TABLE')
        	write_list(flat_sky_list, 'twilight.sof')
		print('Created twilight.sof')
        elif MASTER_BIAS_EXIST == False:
                print('ERROR: MASTER_BIAS does not exist. Can not create wavecal.sof')
                sys.exit(0)
	elif MASTER_FLAT_EXIST == False:
		print('ERROR: MASTER_FLAT does not exist. Can not create wavecal.sof')
		sys.exit(0)
        elif TRACE_TABLE_EXIST == False:
                print('ERROR: TRACE_TABLE does not exist. Can not create wavecal.sof')
                sys.exit(0)
        elif WAVECAL_TABLE_EXIST == False:
                print('ERROR: WAVECAL_TABLE does not exist. Can not create wavecal.sof')
                sys.exit(0)

def create_object_sof():
# object.sof is to be used for muse_scibasic
        if  all([MASTER_BIAS_EXIST == True,  MASTER_FLAT_EXIST == True, TRACE_TABLE_EXIST == True,
		 WAVECAL_TABLE_EXIST == True, TWILIGHT_CUBE_EXIST == True]):
		for i in range(len(object_list)):
			object_list[i] = object_list[i] + ' ' + 'OBJECT'
		object_list.append(illum_list[0] + ' ' + 'ILLUM')
		object_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
		object_list.append(MASTER_FLAT + ' ' + 'MASTER_FLAT')
		object_list.append(TWILIGHT_CUBE + ' ' + 'TWILIGHT_CUBE')
        	object_list.append(TRACE_TABLE + ' ' + 'TRACE_TABLE')
		object_list.append(WAVECAL_TABLE + ' ' + 'WAVECAL_TABLE')
		if BADPIX_TABLE_EXIST == True:
			object_list.append(BADPIX_TABLE + ' ' + 'BADPIX_TABLE')
		object_list.append(GEOMETRY_TABLE + ' ' + 'GEOMETRY_TABLE')
                print ''
		write_list(object_list, 'object.sof')	
        	print('Created object.sof')
        elif MASTER_BIAS_EXIST == False:
                print ''
		print('ERROR: MASTER_BIAS does not exist. Can not create object.sof')
                sys.exit(0)
        elif MASTER_FLAT_EXIST == False:
                print ''
		print('ERROR: MASTER_FLAT does not exist. Can not create object.sof')
                sys.exit(0)
        elif TRACE_TABLE_EXIST == False:
                print ''
		print('ERROR: TRACE_TABLE does not exist. Can not create object.sof')
                sys.exit(0)
        elif WAVECAL_TABLE_EXIST == False:
                print ''
		print('ERROR: WAVECAL_TABLE does not exist. Can not create object.sof')
                sys.exit(0)
	elif TWILIGHT_CUBE_EXIST == False:
		print ''
		print('ERROR: TWILIGHT_CUBE does not exist. Can not create object.sof')
		sys.exit(0)	
	
def create_standard_sof():
# standard.sof is to be used for muse_scibasic
        if  all([MASTER_BIAS_EXIST == True,  MASTER_FLAT_EXIST == True, TRACE_TABLE_EXIST == True,
                 WAVECAL_TABLE_EXIST == True, TWILIGHT_CUBE_EXIST == True]):
		for i in range(len(std_list)):
			std_list[i] = std_list[i] + ' ' + 'STD'
		std_list.append(illum_list[0] + ' ' + 'ILLUM')
		std_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
        	std_list.append(MASTER_FLAT + ' ' + 'MASTER_FLAT')
        	std_list.append(TWILIGHT_CUBE + ' ' + 'TWILIGHT_CUBE')
        	std_list.append(TRACE_TABLE + ' ' + 'TRACE_TABLE')
        	std_list.append(WAVECAL_TABLE + ' ' + 'WAVECAL_TABLE')
		if BADPIX_TABLE_EXIST == True:
	        	std_list.append(BADPIX_TABLE + ' ' + 'BADPIX_TABLE')
        	std_list.append(GEOMETRY_TABLE + ' ' + 'GEOMETRY_TABLE')
        	write_list(std_list, 'standard.sof')
        	print('Created standard.sof')
        elif MASTER_BIAS_EXIST == False:
                print('ERROR: MASTER_BIAS does not exist. Can not create standard.sof')
                sys.exit(0)
        elif MASTER_FLAT_EXIST == False:
                print('ERROR: MASTER_FLAT does not exist. Can not create standard.sof')
                sys.exit(0)
        elif TRACE_TABLE_EXIST == False:
                print('ERROR: TRACE_TABLE does not exist. Can not create standard.sof')
                sys.exit(0)
        elif WAVECAL_TABLE_EXIST == False:
                print('ERROR: WAVECAL_TABLE does not exist. Can not create standard.sof')
                sys.exit(0)
	elif TWILIGHT_CUBE_EXIST == False:
		print('ERROR: TWILIGHT_CUBE does not exist. Can not create standard.sof')
		sys.exit(0)

def create_std_sof():
# std.sof is to be used for muse_standard
	PIXTABLE_STD_list = glob.glob('PIXTABLE_STD_*.fits')
	for i in range(len(PIXTABLE_STD_list)):
		PIXTABLE_STD_list[i] = PIXTABLE_STD_list[i] + ' ' + 'PIXTABLE_STD'
	PIXTABLE_STD_list.append(EXTINCT_TABLE + ' ' + 'EXTINCT_TABLE')
	PIXTABLE_STD_list.append(STD_FLUX_TABLE + ' ' + 'STD_FLUX_TABLE')
	write_list(PIXTABLE_STD_list, 'std.sof')
	print('Created std.sof')

def create_object_sky_sof():
# objectsky.sof is to be used for muse_scibasic
        if  all([MASTER_BIAS_EXIST == True,  MASTER_FLAT_EXIST == True, TRACE_TABLE_EXIST == True,
                 WAVECAL_TABLE_EXIST == True, TWILIGHT_CUBE_EXIST == True]):
		for i in range(len(object_sky_list)):
	                object_sky_list[i] = object_sky_list[i] + ' ' + 'SKY'
		while len(object_sky_list) < num_object:
			object_sky_list.append(object_sky_list[-1])
        	object_sky_list.append(illum_list[0] + ' ' + 'ILLUM')
        	object_sky_list.append(MASTER_BIAS + ' ' + 'MASTER_BIAS')
        	object_sky_list.append(MASTER_FLAT + ' ' + 'MASTER_FLAT')
        	object_sky_list.append(TWILIGHT_CUBE + ' ' + 'TWILIGHT_CUBE')
        	object_sky_list.append(TRACE_TABLE + ' ' + 'TRACE_TABLE')
        	object_sky_list.append(WAVECAL_TABLE + ' ' + 'WAVECAL_TABLE')
        	if BADPIX_TABLE_EXIST == True:
			object_sky_list.append(BADPIX_TABLE + ' ' + 'BADPIX_TABLE')
        	object_sky_list.append(GEOMETRY_TABLE + ' ' + 'GEOMETRY_TABLE')
        	write_list(object_sky_list, 'objectsky.sof')
        	print('Created objectsky.sof')
        elif MASTER_BIAS_EXIST == False:
                print('ERROR: MASTER_BIAS does not exist. Can not create objectsky.sof')
                sys.exit(0)
        elif MASTER_FLAT_EXIST == False:
                print('ERROR: MASTER_FLAT does not exist. Can not create objectsky.sof')
                sys.exit(0)
        elif TRACE_TABLE_EXIST == False:
                print('ERROR: TRACE_TABLE does not exist. Can not create objectsky.sof')
                sys.exit(0)
        elif WAVECAL_TABLE_EXIST == False:
                print('ERROR: WAVECAL_TABLE does not exist. Can not create objectsky.sof')
                sys.exit(0)
        elif TWILIGHT_CUBE_EXIST == False:
                print('ERROR: TWILIGHT_CUBE does not exist. Can not create objectsky.sof')
                sys.exit(0)

def create_sky_sof():
# sky.sof is to be used for muse_create_sky
        if all([LSF_PROFILE_EXIST == True, STD_RESPONSE_EXIST == True, STD_TELLURIC_EXIST == True]):
		PIXTABLE_SKY_list = glob.glob('PIXTABLE_SKY_*.fits')
        	for i in range(len(PIXTABLE_SKY_list)):
                	PIXTABLE_SKY_list[i] = PIXTABLE_SKY_list[i] + ' ' + 'PIXTABLE_SKY'
        	PIXTABLE_SKY_list.append(LSF_PROFILE + ' ' + 'LSF_PROFILE')
		PIXTABLE_SKY_list.append(STD_RESPONSE + ' ' + 'STD_RESPONSE')
        	PIXTABLE_SKY_list.append(STD_TELLURIC + ' ' + 'STD_TELLURIC')
		PIXTABLE_SKY_list.append(EXTINCT_TABLE + ' ' + 'EXTINCT_TABLE')
        	PIXTABLE_SKY_list.append(SKY_LINES + ' ' + 'SKY_LINES')
		write_list(PIXTABLE_SKY_list, 'sky.sof')
        	print('Created sky.sof')

def create_scipost_sof():
# scipost.sof is to be used for muse_scipost
        if all([LSF_PROFILE_EXIST == True, STD_RESPONSE_EXIST == True, STD_TELLURIC_EXIST == True]):
        	PIXTABLE_OBJECT_list = glob.glob('PIXTABLE_OBJECT_*.fits')
        	for i in range(len(PIXTABLE_OBJECT_list)):
                	PIXTABLE_OBJECT_list[i] = PIXTABLE_OBJECT_list[i] + ' ' + 'PIXTABLE_OBJECT'
		PIXTABLE_OBJECT_list.append(LSF_PROFILE + ' ' + 'LSF_PROFILE')
		PIXTABLE_OBJECT_list.append(STD_RESPONSE + ' ' + 'STD_RESPONSE')
		PIXTABLE_OBJECT_list.append(STD_TELLURIC + ' ' + 'STD_TELLURIC')
		PIXTABLE_OBJECT_list.append(ASTROMETRY_WCS + ' ' + 'ASTROMETRY_WCS')
		PIXTABLE_OBJECT_list.append(EXTINCT_TABLE + ' ' + 'EXTINCT_TABLE')
		PIXTABLE_OBJECT_list.append(SKY_LINES + ' ' + 'SKY_LINES')
		PIXTABLE_OBJECT_list.append(FILTER_LIST + ' ' + 'FILTER_LIST')
		if SKY_CONTINUUM_EXIST == True:
			PIXTABLE_OBJECT_list.append(SKY_CONTINUUM + ' ' + 'SKY_CONTINUUM')
		write_list(PIXTABLE_OBJECT_list, 'scipost.sof')       
		print('Created scipost.sof')
	


# PART 4: DATA REDUCTION
# ----------------------

print('---Beginning Data Reduction---')

# MUSE_BIAS
# Creates the master bias. Needs at least 3 bias frames.
if auto_mode == False:
	print ''
	if MASTER_BIAS_EXIST == True:
		perform_bias = raw_input('MASTER_BIAS already exists. Do you still want to perform muse_bias? (y/n)')	

	elif MASTER_BIAS_EXIST == False:
		perform_bias = raw_input('MASTER_BIAS does not exist yet. Perform muse_bias? (y/n)')

# If yes, perform muse_bias
if perform_bias in ('y', 'yes', 'Yes'):
	try:
		create_bias_sof()
		call('echo ---Running muse_bias---', shell=True)
		call('OMP_NUM_THREADS=24 esorex --log-file=bias.log muse_bias --nifu=-1 --merge bias.sof', shell=True)
        	call('echo ---Finished running muse_bias---', shell=True)
		print('MASTER_BIAS.fits was created')
		MASTER_BIAS_EXIST = True
		MASTER_BIAS = science_data_directory + '/MASTER_BIAS.fits'
	except:
		print('ERROR: Could not run muse_bias')
		sys.exit(0)



# MUSE_FLAT
# Creates the master flat. Needs at least 3 lamp flat frames.
if auto_mode == False:
	print ''
        if MASTER_FLAT_EXIST == True:
        	perform_flat = raw_input('MASTER_FLAT already exists. Do you still want to perform muse_flat? (y/n)')

        elif MASTER_FLAT_EXIST == False:
        	perform_flat = raw_input('MASTER_FLAT does not exist yet. Perform muse_flat? (y/n)')


# If yes, perform muse_flat
if perform_flat in ('y', 'yes', 'Yes'):
	try:
		create_flat_sof()
		call('echo ---Running muse_flat---', shell=True)
		call('OMP_NUM_THREADS=24 esorex --log-file=flat.log muse_flat --nifu=-1 --merge flat.sof', shell=True)
        	call('echo ---Finished running muse_flat---', shell=True)
		print('MASTER_FLAT.fits and TRACE_TABLE.fits were created')
		MASTER_FLAT_EXIST = True
		MASTER_FLAT =  science_data_directory + '/MASTER_FLAT.fits'
		TRACE_TABLE_EXIST = True
		TRACE_TABLE =  science_data_directory + '/TRACE_TABLE.fits'
	except:
		print('ERROR: Could not run muse_flat')
		sys.exit(0)



# MUSE_WAVECAL
# Creates the wavecal table. Needs at least 3 wave frames.
if auto_mode == False:
	print ''
	if WAVECAL_TABLE_EXIST == True:
		perform_wavecal = raw_input('WAVECAL_TABLE already exists. Do you still want to perform muse_wavecal? (y/n)')
	
	elif WAVECAL_TABLE_EXIST == False:
		perform_wavecal = raw_input('WAVECAL_TABLE does not exist yet. Perform muse_wavecal? (y/n)')

# If yes, perform muse_wavecal
if perform_wavecal in ('y', 'yes', 'Yes'):
	try:
		create_wavecal_sof()
		call('echo ---Running muse_wavecal---', shell = True)
		call('OMP_NUM_THREADS=24 esorex --log-file=wavecal.log muse_wavecal --nifu=-1 --resample --residuals --merge wavecal.sof', shell = True)
        	call('echo ---Finished running muse_wavecal---', shell = True)
		print('WAVECAL_TABLE.fits was created')
		WAVECAL_TABLE_EXIST = True
		WAVECAL_TABLE =  science_data_directory + '/WAVECAL_TABLE.fits'
	except:
		print('ERROR: Could not run muse_wavecal')
		sys.exit(0)



# MUSE_LSF
# Creates the lsf profile. Needs at least 3 wave frames.
if auto_mode == False:
	print ''
	if LSF_PROFILE_EXIST == True:
		perform_lsf = raw_input('LSF_PROFILE already exists. Do you still want to perform muse_lsf? (y/n)')
	elif LSF_PROFILE_EXIST == False:
		perform_lsf = raw_input('LSF_PROFILE does not exist yet. Perform muse_lsf? (y/n)')

# If yes, perform muse_lsf
if perform_lsf in ('y', 'yes', 'Yes'):
	try:
		create_lsf_sof()
		call('echo ---Running muse_lsf---', shell = True)
		call('OMP_NUM_THREADS=24 esorex --log-file=lsf.log muse_lsf --nifu=-1 --merge lsf.sof', shell = True)	
        	call('echo ---Finished running muse_lsf---', shell = True)
		print('LSF_PROFILE.fits was created')
		LSF_PROFILE_EXIST = True
		LSF_PROFILE =  science_data_directory + '/LSF_PROFILE.fits'
	except:
		print('ERROR: Could not run muse_lsf')
		sys.exit(0)



# MUSE_TWILIGHT
# Creates the twilight cube. Needs at least 3 sky flat frames
if auto_mode == False:
	print ''
	if TWILIGHT_CUBE_EXIST == True:
		perform_twilight = raw_input('TWILIGHT_CUBE already exits. Do you still want to perform muse_twilight? (y/n)')
	elif TWILIGHT_CUBE_EXIST == False:
	        perform_twilight = raw_input('TWILIGHT_CUBE does not exist yet. Perform muse_twilight? (y/n)')

# If yes, perform muse_twilight
if perform_twilight in ('y', 'yes', 'Yes'):
	try:
        	create_twilight_sof()
        	call('echo ---Running muse_twilight---', shell = True)
        	call('OMP_NUM_THREADS=24 esorex --log-file=twilight.log muse_twilight twilight.sof', shell = True)
        	call('echo ---Finished running muse_twilight---', shell = True)
		print('TWILIGHT_CUBE.fits was created')
		TWILIGHT_CUBE_EXIST = True
		TWILIGHT_CUBE =  science_data_directory + '/TWILIGHT_CUBE.fits'
	except:
		print('ERROR: Could not run muse_twilight')
		sys.exit(0)
 

# MUSE_SCIBASIC (for object)
print ''
print '---PRE-PROCESSING---'
# Creates the PIXTABLES for the object. These will be used to reduce the exposure.
if auto_mode == False:
	print ''
        perform_scibasic_object = raw_input('Perform muse_scibasic for object? (y/n)')

# If yes, perform muse_scibasic for object
if perform_scibasic_object in ('y', 'yes', 'Yes'):
	try:
        	create_object_sof()
        	call('echo ---Running muse_scibasic for object---', shell = True)
        	call('OMP_NUM_THREADS=24 esorex --log-file=object.log muse_scibasic --nifu=-1 --merge object.sof', shell = True)
        	call('echo ---Finished running muse_scibasic for object---', shell = True)
	except:
		print('ERROR: Could not run muse_scibasic for object')	
		sys.exit(0)

	
# MUSE_STANDARD
print ''
print '---FLUX CALIBRATION---'
# Two parts, muse_scibasic (for std) and muse_standard. 
# These will create the standard PIXTABLES then use them to create the STD response and STD telluric. 
if auto_mode == False:
	print ''
        perform_scibasic_std = raw_input('Perform muse_scibasic for standard? (y/n)')
	
# If yes, perform muse_scibasic for standard
if perform_scibasic_std in ('y', 'yes', 'Yes'):
        try:
		create_standard_sof()
        	call('echo ---Running muse_scibasic for standard---', shell = True)
        	call('OMP_NUM_THREADS=24 esorex --log-file=standard.log muse_scibasic --nifu=-1 --merge standard.sof', shell = True)
        	call('echo ---Finished running muse_scibasic for standard---', shell = True)
	except:
		print('ERROR: Could not run muse_scibasic for standard')
		sys.exit(0)


if auto_mode == False:
        print ''
        perform_standard = raw_input('Perform muse_standard? (y/n)')

#If yes, perform muse_standard
if perform_standard in ('y', 'yes', 'Yes'):
	try:	
		create_std_sof()
        	call('echo ---Running muse_standard---', shell = True)
        	call('OMP_NUM_THREADS=24 esorex --log-file=std.log muse_standard --filter=white std.sof', shell = True)
        	call('echo ---Finished running muse_standard---', shell = True)
	except:
		print('ERROR: Could not run muse_standard')
		sys.exit(0)


# MUSE_CREATE_SKY
# This is to be used when the galaxy fills the entier field of view.
print ''
print '---SKY CREATION---'
if auto_mode == False:
	print ''
	print 'Sky creation is not required if the object does not completly fill the field of view.'
	perform_scibasic_sky = raw_input('Perform muse_scibasic for sky? (y/n)')
	
# If yes, perform muse_scibasic for sky
if perform_scibasic_sky in ('y', 'yes', 'Yes'):
        try:
                create_object_sky_sof()
                call('echo ---Running muse_scibasic for sky---', shell = True)
                call('OMP_NUM_THREADS=24 esorex --log-file=objectsky.log muse_scibasic --nifu=-1 --merge objectsky.sof', shell = True)
                call('echo ---Finished running muse_scibasic for sky---', shell = True)
        except:
                print('ERROR: Could not run muse_scibasic for sky')
                sys.exit(0)

if auto_mode == False:
        print ''
        perform_create_sky = raw_input('Perform muse_create_sky? (y/n)')

# If yes, perform muse_create_sky
if perform_create_sky in ('y', 'yes', 'Yes'):
        try:
                create_sky_sof()
                call('echo ---Running muse_create_sky---', shell = True)
                call('OMP_NUM_THREADS=24 esorex --log-file=sky.log muse_create_sky sky.sof', shell = True)
                call('echo ---Finished running muse_create_sky---', shell = True)
		SKY_CONTINUUM_EXIST = True
		SKY_CONTINUUM =  science_data_directory + 'SKY_CONTINUUM.fits'
        except:
                print('ERROR: Could not run muse_create_sky')
                sys.exit(0)


# MUSE_SCIPOST
print ''
print '---POST PROCESSING---'
if auto_mode == False:
	print ''
	perform_scipost = raw_input('Perform muse_scipost? (y/n)')
	print ''

# If yes, perform muse_scipost
if perform_scipost in ('y', 'yes', 'Yes'):
	try:
		create_scipost_sof()
		call('echo ---Running muse_scipost---', shell = True)
		call('OMP_NUM_THREADS=24 esorex --log-file=scipost.log muse_scipost --filter=white,Johnson_V,Cousins_R,Cousins_I scipost.sof', shell = True)
		call('echo ---Finished running muse_scipost---', shell = True)
	except:
		print('ERROR: Could not run muse_scipost')
		sys.exit(0)