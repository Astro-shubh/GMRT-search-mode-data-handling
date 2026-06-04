#!/usr/bin/env python3
import sys
import os
import numpy as np
from sigpyproc.readers import FilReader

# Consistent dispersion constant used natively by sigpyproc (MHz^2 pc^-1 cm^3 s)
DISP_CONSTANT = 4.148808e3

def get_max_delay_samples(header, dm):
    """Calculate the absolute maximum dispersion delay across the band in samples."""
    f1 = header.fch1
    f2 = header.fch1 + (header.nchans - 1) * header.foff
    delay_sec = DISP_CONSTANT * dm * abs(1.0 / (f1**2) - 1.0 / (f2**2))
    return int(np.ceil(delay_sec / header.tsamp))

def frequency_scrunch_with_loop(data_matrix, factor=4):
    """Collapses the frequency axis by looping over channel blocks."""
    orig_nchans, nsamps = data_matrix.shape
    new_nchans = orig_nchans // factor
    scrunched_matrix = np.empty((new_nchans, nsamps), dtype=data_matrix.dtype)
    for new_ch in range(new_nchans):
        start_orig_ch = new_ch * factor
        end_orig_ch = start_orig_ch + factor
        scrunched_matrix[new_ch] = data_matrix[start_orig_ch:end_orig_ch, :].mean(axis=0)
    return scrunched_matrix

def re_disperse_channels(scrunched_matrix, inv_shifts):
    """Manually re-disperses a 2D matrix back to its raw dispersive delay paths."""
    new_nchans, nsamps = scrunched_matrix.shape
    redispersed_matrix = np.empty_like(scrunched_matrix)
    for ch in range(new_nchans):
        shift = inv_shifts[ch]
        if shift != 0:
            redispersed_matrix[ch] = np.roll(scrunched_matrix[ch], shift)
            redispersed_matrix[ch, :shift] = 0
        else:
            redispersed_matrix[ch] = scrunched_matrix[ch]
    return redispersed_matrix

def main_pipeline(input_file, output_file, dm, fscrunch_factor=4, block_size=1000000):
    print(f"Opening file: {input_file}")
    
    input_file_bytes = os.path.getsize(input_file)
    input_file_mb = input_file_bytes / (1024 * 1024)
    print(f"Original Input File Size: {input_file_mb:.2f} MB")

    fil = FilReader(input_file)
    max_shift = get_max_delay_samples(fil.header, dm)
    print(f"Calculated maximum dispersion delay (max_shift): {max_shift} samples.")

    new_nchans = fil.header.nchans // fscrunch_factor
    new_foff = fil.header.foff * fscrunch_factor
    
    # Pre-calculate re-dispersion shift arrays for the NEW wide channels
    wide_freqs = np.linspace(fil.header.fch1, fil.header.fch1 + (new_nchans - 1) * new_foff, new_nchans)
    f_ref = max(wide_freqs)
    inv_delays = DISP_CONSTANT * dm * (1.0 / (wide_freqs**2) - 1.0 / (f_ref**2))
    inv_shifts = np.round(inv_delays / fil.header.tsamp).astype(int)

    out_file = fil.header.prep_outfile(output_file, updates={'nchans': new_nchans, 'foff': new_foff})
    
    total_samples = fil.header.nsamples
    chunk_idx = 0
    print(f"Processing {total_samples} samples using Symmetrical Absolute Overlap-Save...\n")

    current_start = 0

    # Main sequential rendering timeline loop
    while current_start < (total_samples - max_shift):
        
        if chunk_idx == 0:
            # Block 0: Start at index 0. 
            # We must cut out the first max_shift samples because they lack history to roll back.
            read_start = 0
            read_nsamps = min(block_size + max_shift, total_samples)
            
            trim_start = max_shift
            trim_end = read_nsamps
            
            # Absolute write range maps to: [max_shift to block_size + max_shift]
            next_absolute_start = block_size + max_shift
        else:
            # Middle & Arbitrary Last Blocks: Look back exactly max_shift samples
            read_start = current_start - max_shift
            
            # Read ahead standard window block, capped strictly at the end of the file
            read_nsamps = block_size + 2 * max_shift
            if (read_start + read_nsamps) > total_samples:
                read_nsamps = total_samples - read_start
            
            # Discard both max_shift margins symmetrically
            trim_start = max_shift
            trim_end = read_nsamps - max_shift
            
            # Absolute write range maps exactly to: [current_start to current_start + block_size]
            next_absolute_start = read_start + trim_end

        # Fail-safe termination logic
        if read_nsamps <= 0 or (trim_start >= trim_end):
            break

        # A. Read Overlapped Block from storage
        data_block = fil.read_block(start=read_start, nsamps=read_nsamps)
        
        # B. Native Dedispersion
        dedispersed_block = data_block.dedisperse(dm)

        # C. Frequency Collapse (Channel Loop)
        scrunched_data = frequency_scrunch_with_loop(dedispersed_block.data, fscrunch_factor)

        # D. Manual Re-dispersion
        redispersed_data = re_disperse_channels(scrunched_data, inv_shifts)

        # E. Slice out the pristine, padding-free inner zone
        final_chunk_to_write = redispersed_data[:, trim_start:trim_end]
        actual_written_len = final_chunk_to_write.shape[1]

        if actual_written_len <= 0:
            break

        # F. Pure 8-Bit Quantization
        chunk_mean = np.mean(final_chunk_to_write)
        chunk_std  = np.std(final_chunk_to_write)
        if chunk_std == 0: chunk_std = 1.0
            
        target_mean = 128.0
        target_std  = 25.0
        normalized = (final_chunk_to_write - chunk_mean) / chunk_std
        quantized_floats = (normalized * target_std) + target_mean
        
        final_8bit_chunk = np.clip(quantized_floats, 0, 255).astype(np.uint8)
        flat_stream_to_write = final_8bit_chunk.T.flatten()

        if chunk_idx == 0:
            print("="*60)
            print(f"SHAPE TRACKING FOR FIRST OVERLAP BLOCK")
            print("="*60)
            print(f"Raw read boundaries on disk       : {read_start} to {read_start + read_nsamps}")
            print(f"Matrix shape after processing     : {redispersed_data.shape}")
            print(f"Slicing window used (trim indices): {trim_start} to {trim_end}")
            print(f"Final safe chunk shape written    : {final_chunk_to_write.shape}")
            print(f"Next Absolute Stream Sync Point   : Sample {next_absolute_start}")
            print("="*60 + "\n")

        # Write pristine byte stream to file
        out_file.cwrite(flat_stream_to_write)
        
        # --- PHYSICAL FILE SIZE CHECK ---
        out_file.file_obj.flush()
        current_bytes = os.path.getsize(output_file)
        size_percentage = (current_bytes / input_file_bytes) * 100
        current_mb = current_bytes / (1024 * 1024)
        
        # Absolute timeline jumping logic (fixes the block 0/1 seam discontinuity)
        current_start = next_absolute_start
        chunk_idx += 1
        
        print(f"  Block {chunk_idx:03d} | Absolute File Cursor Sync: {current_start:,}/{total_samples:,} | Output Size: {current_mb:.2f} MB ({size_percentage:.2f}% of input file)", end='\r')

    out_file.close()
    final_bytes = os.path.getsize(output_file)
    final_percentage = (final_bytes / input_file_bytes) * 100
    expected_shortened_samps = total_samples - (2 * max_shift)
    
    print(f"\n\nSuccessfully generated finalized pipeline file: {output_file}")
    print(f"Actual Written Samples : {current_start - max_shift:,}")
    print(f"Expected Target Samples: {expected_shortened_samps:,} (Shorter by exactly 2 * max_shift)")
    print(f"Final Total File Size  : {final_bytes / (1024 * 1024):.2f} MB ({final_percentage:.2f}% of input file)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python script.py input_file output_file dm fscrunch_factor [block_size]")
        sys.exit(1)
        
    bsize = int(sys.argv[5]) if len(sys.argv) > 5 else 1000000
    main_pipeline(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), bsize)
