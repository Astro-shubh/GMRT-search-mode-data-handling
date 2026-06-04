import argparse, os, sys
from Processing_modules.process_modules import *
from Processing_modules.processGMRT_global import *
import logging

#path_data = "/raid/scratch/ssingh/uGMRT_monitoring/10May2025/"

path_data = "../uGMRT_database/10May2025/"

log_file_name = path_data+'process.log'
# Set up logging to both console and file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.FileHandler(log_file_name), logging.StreamHandler()])


path_ugmrt2fil, path_par, path_rficlean, keep_filterbank, make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive,make_1c_subintegrated_archive, make_sp_low_res_subbands, make_sp_low_res_1ch, make_sp_high_res_subbands, make_sp_high_res_1ch, nbin, ncha, subint_len, nbinsp, nchasp, dspsr_threads, do_RFI_clean, keep_rfi_clean = global_variables()


logging.info(f"Going to process the pulsar data in the area {path_data}")
if os.path.exists(path_par) == True:
    logging.info(f"Path to the parfle found. PATH ={path_par}")

if keep_filterbank == 1:
    logging.info(f"\n Filterbank file will be saved.")
if keep_filterbank == 0:
    logging.info(f"\n Filterbank file will be deleted at the end of the data processing.")

if do_RFI_clean == 1:
    logging.info(f"\n RFIclean code will be used to clean the RFI from the data")
if do_RFI_clean == 0:
    logging.info(f"\n RFIclean code will not be used to clean the RFI from the data")

if keep_rfi_clean == 1:
    logging.info(f"\n RFI cleaned fil file will be saved.")
if keep_rfi_clean == 0:
    logging.info(f"\n RFI cleaned fil file will be deleted.")

if make_folded_archive_subband_subint == 1:
    logging.info(f"\n Folded subintegrated and sub-banded data will be produced.")
if make_folded_archive_subband_subint == 0:
    logging.info(f"\n Folded subintegrated and sub-banded data will be deleted.")

if make_1t_1c_archive == 1:
    logging.info(f"\n Archives with single channel and single time integration will be produced.")
if make_1t_1c_archive == 0:
    logging.info(f"\n Archives with single channel and single time integration will not be produced.")

if make_1t_subbanded_archive == 1:
    logging.info(f"\n Archives collapsed in the time axis but with subbands will be produced.")
if make_1t_subbanded_archive == 0:
    logging.info(f"\n Archives collapsed in the time axis but with subbands will not be produced.")

if make_1c_subintegrated_archive ==1:
    logging.info(f"\n Archives collapsed in frequncy but with subintegrations will be produced.")
if make_1c_subintegrated_archive ==0:
    logging.info(f"\n Archives collapsed in frequncy but with subintegrations will not be produced.")

if make_sp_low_res_subbands == 1:
    logging.info(f"\n Single pulse archives with low resolution will be produced with subbands.")
if make_sp_low_res_subbands == 0:
    logging.info(f"\n Single pulse archives with low resolution will be produced with subbands with all not be produced.")

if make_sp_low_res_1ch == 1:
    logging.info(f"\n Single pulse archives with low resolution and all freq channels collapsed will be produced.")
if make_sp_low_res_1ch == 0:
    logging.info(f"\n Single pulse archives with low resolution and all freq channels collapsed will not be produced.")

if make_sp_high_res_subbands == 1:
    logging.info(f"\n Single pulse archives with high resolution and subbands will be produced.")
if make_sp_high_res_subbands == 0:
    logging.info(f"\n Single pulse archives with high resolution and subbands will not be produced.")

if make_sp_high_res_1ch == 1:
    logging.info(f"\n Single pulse archives with high resolution and all freq channels will be produced.")
if make_sp_high_res_1ch == 0:
    logging.info(f"\n Single pulse archives with high resolution and all freq channels will not be produced.")


logging.info(f"\n ========= Processing parameters Fold mode data ============\n")

logging.info(f"\n Number of bins across the pulse profile is = {nbin}")
logging.info(f"\nIf sub-banded data is requested.")
logging.info(f"\n NCHAN = {ncha}")

logging.info(f"\nIf sub-integrated data is requested.")
logging.info(f"\n Lengh of each sub-integration will be = {subint_len} seconds.")

logging.info(f"\n ========= Processing parameters for single pulse data ============\n")
logging.info(f"\n If requested for single pulse file with low resolution then:")
logging.info(f"\n Number of bins across the profile will be = {nbinsp}")
logging.info(f"\n If requested for single pulse file with low resolution then along with subbands are requested then:")
logging.info(f"\n Number of channels = {nchasp}")
logging.info(f"\n If high resolution single pulse data is requested then the number of bins will be decided dynamically based on the sampling time and the pulse period of the pulsar.")
logging.info(f"\n If high resolution single pulse data is requested along with the subbands the archive will have {nchasp} channels.")
logging.info(f"\n ========= *********************** ============\n")
logging.info(f"\n ========= *********************** ============\n")

#predicted_P = get_P(path_par+'J1830-1059.par', 60999.9)
#print (predicted_P)
#sys.exit()

def is_file_empty(file_path):
    sig = 1
    size = os.path.getsize(file_path)
    if size == 0:
        sig = 0
    return sig
    


pairs = find_raw_pairs(path_data)
print ("Pairs :", pairs)
outbits=8
#sys.exit()
for j in pairs:
    header_file = j[1]
    raw_file = j[0]
    logging.info(f"\n Header file: {header_file}")
    logging.info(f"\n Raw data file: {raw_file}")
    sig = is_file_empty(header_file)
    if sig == 0:
        logging.info(f"\n Header file is empty so this source will not be processed:")
        logging.info(f"\n Moving to the next source.")
    if sig == 1:
        source, Ch, freq, samp_time, chwd, bandwidth, LSB, USB, mjd, inbits = get_hdr_param(header_file)
        logging.info(f"\n===============Will process for the PSR {source}.==============")
        filterbank_extension = '.fil'
        filebase = source+'.'+freq+'.'+mjd+'.'+bandwidth
        out_fil_file = filebase+filterbank_extension
        outfile_w_path = os.path.join(path_data, out_fil_file)
        

        ## check if the fil file exists..
        fil_exists = os.path.exists(outfile_w_path)
        if fil_exists == True:
            print ("Filterbank file exists in the directory and hence the new file won't be produced.")
            logging.info(f"\n Filterbank file exists in the directory and hence the new file won't be produced.") 
        if fil_exists == False:
            logging.info(f"\nName of the filterbank file: {out_fil_file}")
            logging.info(f"\n Started making filterbank file for the PSR {source}.")
            xx = make_filterbank(path_ugmrt2fil, path_data, raw_file, outfile_w_path, source, mjd, freq, Ch, chwd, samp_time, USB, inbits, outbits)
            logging.info(f"\n Filterbank file produced.") 
        if do_RFI_clean == 1:
           filebase = source+'.'+freq+'.'+mjd+'.'+bandwidth
           rfi_clean_ext = '.rficlean.fil'
           out_rfi_cln_file = filebase+rfi_clean_ext
           input_fil_file = outfile_w_path
           out_rfi_clean_w_path = os.path.join(path_data, out_rfi_cln_file)
           logging.info(f"\n Will do RFI cleaning")

           rfi_clean_exists = os.path.exists(out_rfi_cln_file)
           if rfi_clean_exists == True:
               print ("RFI cleaned Filterbank file exists in the directory and hence the new file won't be produced.")
               logging.info(f"\n RFI cleaned Filterbank file exists in the directory and hence the new file won't be produced.") 
           if rfi_clean_exists == False:
               yy = RFI_clean(path_rficlean, input_fil_file, out_rfi_clean_w_path, time_samps=16384, freq_clean_th=3.0, zerodm=True)
               
               logging.info(f"\n RFI Clean file produced.")
               if keep_filterbank == 0 and keep_rfi_clean == 1:
                   comms = f"rm {outfile_w_path}"
                   os.system(comms)

        ### =========== This part of the code will make the archive files ===============###
        ### =========== First we focus on the fold mode observations to process =========###
        #, make_sp_low_res_subbands, make_sp_low_res_1ch, make_sp_high_res_subbands, make_sp_high_res_1ch, nbin, ncha, subint_len, nbinsp, nchasp

        if all(x == 0 for x in [make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive]):
            logging.info(f"\n No folded profiles archives will be produced as all the keys for the folded are set to 0.\n")
        if any(x == 1 for x in [make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive]):
            logging.info(f"\n Requeseted folded data product will be produced.\n")
            parfile = path_par+source+'.par'
            if os.path.exists(parfile):
                logging.info(f"\nPar file for the pulsar {source} found. Will be used for folding the data.")
                if keep_filterbank == 0 and keep_rfi_clean == 1:
                    fil_file_to_use = out_rfi_clean_w_path
                if keep_filterbank == 1 and keep_rfi_clean == 0:
                    fil_file_to_use = outfile_w_path
                if keep_filterbank == 1 and keep_rfi_clean == 1:
                    fil_file_to_use = out_rfi_clean_w_path
                    print (f"Consider deleting file: {outfile_w_path} occupying too much space.")
                if keep_filterbank == 0 and keep_rfi_clean == 0:
                    print ("Invalid argument")
                    sys.exit()

                make_archive(source, mjd, fil_file_to_use, path_data, parfile, filebase, make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive, make_sp_low_res_subbands, make_sp_low_res_1ch, make_sp_high_res_subbands, make_sp_high_res_1ch, nbin, ncha, subint_len, nbinsp, nchasp, dspsr_threads,freq, bandwidth)
            else:
                print("Parameter file not found.")
        
    if keep_filterbank == 0 and keep_rfi_clean == 1:
        comms = f"rm {outfile_w_path}"
        os.system(comms)




    
