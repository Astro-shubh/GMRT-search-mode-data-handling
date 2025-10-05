import os 

################ defining global variables ################

def global_variables():
    """
    This module has all the global variables input required for 
    processGMRT code needs to know to reduce the data to psrchive format

    Advice for ideal combination of parameters:
    keep make_sp_low_res_subbands = 1
    make_sp_low_res_1ch = 0 # as you can always collapse the bands after DM corrections.
    But if you are confident about the DM being correct then possibly 

    """
    #### Paths to all code par file directory
    path_ugmrt2fil = "/raid/scratch/ssingh/uGMRT_monitoring/CODES/ugmrt2fil/"
    path_par = "/raid/scratch/ssingh/uGMRT_monitoring/CODES/gmrt_pipeline/parfiles/"

    #### Options to keep or remove the filterbank file ########
    keep_filterbank = 1 # make it to 0 if you do not want to save the filterbank file.

    ###### Options for the folded mode data reduction ############
    nbin = 1024
    ncha = 128
    subint_len = 5 ## in seconds.... this variable is the length of ech subintegration. It could be a problem for long period pulsars.
    make_folded_archive_subband_subint = 1 # make it to 0 if you do not want to make the folded subbanded and subintegrated archive.
    make_1t_1c_archive = 1 # make it to 0 if you do not want to make an archive with only 1 channel and 1 integration.
    make_1t_subbanded_archive = 1 # make it to 0 if you do not want to make an archive collapsed in time but just with subbands.
    make_1c_subintegrated_archive = 1 # make it to 0 if you not want to make an archive collapsed in freq but with sunintegartions.

    ###### Options for the single pulse mode data reduction ###########
    #### In this case the number of bins will be determined dynamically based on the pulse period and the sampling time ####
    #### The function for the dynamical determination of bin size for this case can be found in the code process_modules.py ####
    #### But for the low resolution data it will be kept to 1024 bins and 64 bands #####
    nbinsp = 1024
    nchasp = 64
    make_sp_low_res_subbands = 1 # make it to 0 if you do not want to have subbanded single pulse file with default low resolution.
    make_sp_low_res_1ch = 1 # make it to 0 if you do not want to have single pulse file with low resolution all scrunched in freq.

    #### The single pulse parameter are only useful if you want to produce data for studies of microstructure.#####
    
    make_sp_high_res_subbands = 1 # make it to 0 if you do not want the single pulse with the highest resolution with subands.###
    make_sp_high_res_1ch = 1 # make it to 0 if you do not want the singe pulse with the highest resolution with band scrunched. ####
     
    dspsr_threads = 32

    return path_ugmrt2fil, path_par, keep_filterbank, make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive, make_sp_low_res_subbands, make_sp_low_res_1ch, make_sp_high_res_subbands, make_sp_high_res_1ch, nbin, ncha, subint_len, nbinsp, nchasp, dspsr_threads






