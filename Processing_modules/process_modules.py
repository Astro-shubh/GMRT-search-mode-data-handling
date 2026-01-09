import os, sys
import numpy as np
from datetime import datetime, timedelta
from astropy.time import Time
from decimal import Decimal, ROUND_DOWN


def ist2mjd(ist_datetime_str):
    """
    Convert IST datetime string with nanosecond precision to MJD,
    using Astropy's Time class for high-precision handling.
    """
    # Convert IST to UTC manually by subtracting 5.5 hours (IST = UTC + 5.5h)
    t_ist = Time(ist_datetime_str, scale='utc') - 5.5 / 24.0
    return t_ist.mjd




def find_raw_pairs(directory, pulsar=None):
    """
    This function will give you the pair of 
    *.raw and *.raw.ahdr files in the 
    given <directory> provided as the 
    input.
    """
    # Store found files
    raw_files = set()
    hdr_files = set()

    # Walk through the directory
    for file in os.listdir(directory):
        if file.endswith(".raw"):
            raw_files.add(os.path.splitext(file)[0])
        elif file.endswith(".raw.ahdr"):
            hdr_files.add(os.path.splitext(file)[0].replace(".raw", ""))

    # Find matching base names
    pairs = []
    for base in raw_files & hdr_files:
        if pulsar is None or pulsar in base:
            raw_path = os.path.join(directory, base + ".raw")
            hdr_path = os.path.join(directory, base + ".raw.ahdr")
            pairs.append((raw_path, hdr_path))

    return pairs



def get_hdr_param(hdr_file):
    LSB = False
    USB = False
    with open(hdr_file, "r") as hdr:
        for line in hdr:
            #print (line.split("="))
            if "=" not in line:
                continue  # skip malformed lines
            key = line.split("=")[0]
            val = line.split("=")[1].lstrip().split("\n")[0]
            if key == "Source                     ":
                source = val
            if key == "Channels                   ":
                Ch = val
            if key == "Frequency Ch.1  (Hz)       ":
                freq = str(float(val)/1e6)
            if key == "Sampling time  (uSec)      ":
                samp_time = Decimal(float(val)*1e-6).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
                samp_time = str(samp_time)
            if key == "Bandwidth (MHz)            ":
                bandwidth = str(float(val))
            if key == "Channel width (Hz)         ":
                Ch_wd = abs(float(val)*1e-6)
                ch_sign = np.sign(float(val))
                if ch_sign > 0:
                    LSB = True
                if ch_sign < 0:
                    USB = True
            if key == "Date                       ":
                date = val
            if key == "IST Time                   ":
                ist = val
            if key == "Num bits/sample            ":
                inbits = val

    Date_split = date.split("/")
    date_format = Date_split[2]+"-"+Date_split[1]+"-"+Date_split[0]+" "+ist
    mjd = str(ist2mjd(date_format))
    return [source, Ch, freq, samp_time, Ch_wd, bandwidth, LSB, USB, mjd, inbits]



def make_filterbank(pathcode, path_data, infile, outfile, jname, mjd, freq, nchan, chwd, tsmpl, usb, inbits, outbits):
    code_lsb = pathcode+'./ugmrtlsb2fil'
    code_usb = pathcode+'./ugmrtusb2fil'
    if usb == False:
        print("Running ugmrt2fil for LSB.")
#        headfile = path_data+os.path.basename(outfile) + ".head"
#        command = code_lsb+" {} {} {} {} {} {} {} {} {}".format(infile, outfile, jname, mjd, freq, nchan, chwd, tsmpl, headfile)
        command = code_lsb+" {} {} {} {} {} {} {} {} {} {}".format(infile, outfile, jname, mjd, freq, nchan, chwd, tsmpl, inbits, outbits)
        print (command)
        os.system(command)
#        command2 = "cat {} {} > {}".format(headfile, infile, outfile)
#        print (command2)
#        os.system(command2)
#        command3 = "rm {}".format(headfile)
#       print (command3)
#        os.system(command3)
    else:
        print("Running ugmrt2fil for USB.")
#        command = code_usb+" {} {} {} {} {} {} {} {}".format(infile, outfile, jname, mjd, freq, nchan, chwd, tsmpl)
        command = code_usb+" {} {} {} {} {} {} {} {} {} {}".format(infile, outfile, jname, mjd, freq, nchan, chwd, tsmpl, inbits, outbits)
        print (command)
        os.system(command)
    return None



def make_archive(Jname, sttime, filfile, path_data, parfile, outfile, make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive, make_sp_low_res_subbands, make_sp_low_res_1ch, make_sp_high_res_subbands, make_sp_high_res_1ch, nbin, ncha, subint_len, nbinsp, nchasp, dspsr_threads):
    ### First dealing with the fold mode products ##########
    if any(x == 1 for x in [make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive]):
        print ("Will make the folded data product.")
        master_out_archive =path_data+Jname+".master"
        command_master_dspsr_fold = f"dspsr {filfile} -N {Jname} -b {nbin} -E {parfile} -L {subint_len} -m {sttime} -A -e ar -t {dspsr_threads} -d 1 -k gmrt -O {master_out_archive}"
        print (command_master_dspsr_fold)
        os.system(command_master_dspsr_fold)
        if make_folded_archive_subband_subint == 1:
            folded_subint_subband_file = path_data+outfile+"_subint_"+str(ncha)+'_ch.ar'
            command_subint_subband = f"pam --setnchn {ncha} {master_out_archive}.ar -e new"
            os.system(command_subint_subband)
            #print (command_subint_subband)
            command21 = f"mv {master_out_archive}.new {folded_subint_subband_file}"
            os.system(command21)
            #print (command21)


    #if all(x == 1 for x in [make_folded_archive_subband_subint, make_1t_1c_archive, make_1t_subbanded_archive, make_1c_subintegrated_archive]):



    return None


'''
foldmode=False, singlepulse=False):
    """
    Run the dspsr command for making the foldmode data, single pulse etc 
    """

#dspsr -N J1645-0317 -b 1024 -E J1645-0317.good.par -L 5 -m 60806.436465399223 -A J1645-0317_550_200_bm1_10May2025.check.fil -O testing -e ar -t 32 -K -d 1 -k gmrt

'''



def get_P(parfile, predT):
    with open(parfile) as f:
        for line in f:
            if line.startswith('F0'):
                F0 = line.split()[1]
            elif line.startswith('F1'):
                F1 = line.split()[1]
            elif line.startswith('F2'):
                F2 = line.split()[1]
            elif line.startswith('PEPOCH'):
                PEPOCH = line.split()[1]
    f0 = float(F0)
    f1 = float(F1)
    f2 = float(F2)
    t0 = float(PEPOCH)
    mjd2sec = 86400.0
    dt = predT - t0
    DT = dt * mjd2sec
    pred_F = f0 + f1*DT + 0.5 *f2*DT*DT
    pred_P = 1./pred_F
    return pred_P











#/raid/scratch/ssingh/uGMRT_monitoring/CODES/ugmrt2fil/./ugmrtfilhead /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448_1260_200_bm2_10May2025.raw /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448.1460.0.60805.56568429603.200.0.fil J0729-1448 60805.56568429603 1460.0 512 0.390625 0.00002048 /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448.1460.0.60805.56568429603.200.0.fil.head
#cat /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448.1460.0.60805.56568429603.200.0.fil.head /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448_1260_200_bm2_10May2025.raw > /raid/scratch/ssingh/uGMRT_monitoring/10May2025/J0729-1448.1460.0.60805.56568429603.200.0.fil







