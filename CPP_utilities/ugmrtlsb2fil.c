#include "filhead.h"
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void reverse_channels8bits(uint8_t *data, int nchan){
    int i, j;
    uint8_t tmp;
    
    for(i=0; i<nchan/2; i++){
        j = nchan-i-1;
        tmp = data[i];
        data[i] = data[j];
        data[j] = tmp;
    }
}

void reverse_channels16bits(uint16_t *data, int nchan){
    int i, j;
    uint16_t tmp;

    for(i=0; i<nchan/2; i++){
        j = nchan-i-1;
        tmp = data[i];
        data[i] = data[j];
        data[j] = tmp;
    }
}

void _16to8bits(uint16_t *data, uint8_t *buffer8bit, int nchan){
    int i;
    uint8_t value;
    for(i=0; i<nchan; i++){
        value = data[i];
        buffer8bit[i] = value/16.0;
    }
}
        

int main(int argc, char **argv){

    char infilename[150], outfilename[150];
    char jname[20];
    double mjd, freq, bw, tsmpl;
    int nchan, inbits, outbits;
    
    long infile_size, Nsmpl, ismpl;
    int data_size;
    
    if(argc != 11){
        fprintf(stderr, "Invalid number of arguments.\n");
	printf("./EXECUTATBLE <inputfile> <output_fil> <jname> <mjd> <firstchan_freq (MHz)> <num_chans> <chan_width (MHz)> <tsamp (s)> <inbits> <outbits>\n");
        exit(1);
    }
    
    //infile, outfile, jname, mjd, freq, nchan, bw, tsmpl
    strcpy(infilename,  argv[1]);
    strcpy(outfilename, argv[2]);
    strcpy(jname,       argv[3]);
    mjd     = atof(argv[4]);
    freq    = atof(argv[5]);
    nchan   = atoi(argv[6]);
    bw      = atof(argv[7]);
    tsmpl   = atof(argv[8]);
    inbits  = atoi(argv[9]);
    outbits = atoi(argv[10]);
    
    if(mjd==0 || freq<=0 || nchan<=0 || bw==0 || tsmpl<=0 || outbits>inbits){
        fprintf(stderr, "Invalid arguments found.\n");
        exit(1);
    }
    
    FILE *infile = fopen(infilename, "rb");
    if(infile==NULL){
        fprintf(stderr, "Error opening file %s for reading.\n", infilename);
        exit(1);
    }
    
    FILE *outfile = fopen(outfilename, "wb");
    if(outfile==NULL){
        fprintf(stderr, "Error opening file %s for writing.\n", outfilename);
        exit(1);
    }

    if(inbits == 8){
        data_size = sizeof(uint8_t)*nchan;
    }
    else{
        data_size = sizeof(uint16_t)*nchan;
    }
    
    fseek(infile, 0, SEEK_END);
    infile_size = ftell(infile);
    fseek(infile, 0, SEEK_SET);
    if((infile_size%data_size) != 0){
        fprintf(stderr, "The input file size is incompatible with given nchan.\n");
        exit(1);
    }
    
    Nsmpl = infile_size/data_size;
    
    filterbank_header(outfile, infilename, jname, mjd, freq, bw, nchan, tsmpl, outbits);
    uint8_t *data8bit;
    data8bit = (uint8_t*)malloc(nchan*sizeof(uint8_t));
    uint16_t *data16bit;
    data16bit = (uint16_t*)malloc(nchan*sizeof(uint16_t));
    uint8_t *buffer8bit;
    buffer8bit = (uint8_t*)malloc(nchan*sizeof(uint8_t));
        
    for(ismpl=0; ismpl<Nsmpl; ismpl++){
        if(inbits == 8){
            fread(data8bit, sizeof(uint8_t), nchan, infile);
            if(outbits == 8){
                fwrite(data8bit, sizeof(uint8_t), nchan, outfile);
            }
            else{
                printf("Can't convert uint8_t to uint16_t");
                exit(1);
            }
        }
        else{
            fread(data16bit, sizeof(uint16_t), nchan, infile);
            if(outbits == 8){
//                _16to8bits(data16bit, buffer8bit, nchan);
//                fwrite(buffer8bit, sizeof(uint8_t), nchan, outfile);
                int ii;
                for(ii=0; ii<nchan; ii++){ 
                    uint8_t value;
                    value = data16bit[ii]/128.0;   
            	    fwrite(&value, sizeof(value), 1, outfile);
                }
            }
            else{
                fwrite(data16bit, sizeof(uint16_t), nchan, outfile);
            }

        }
    } 
    
    free(data16bit);
    free(data8bit);
    free(buffer8bit);
    
    fclose(infile);
    fclose(outfile);
    
    return 0;
}
