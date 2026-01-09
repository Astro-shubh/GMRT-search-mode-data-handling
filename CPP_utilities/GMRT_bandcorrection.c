#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
int main(int argc, char *argv[])
	{
	char filename1[200],filename2[200];
	if (argc < 5){
		printf("./EXECUTABLE <filename_in> <bandcorrected_filename_out>  <total_samples> <blocksize_in_samples> <num_channels> <numbits_in> <numbits_out>\n");
		exit(1);
	}

	int inbits, outbits;
	long int i=0, j=0, k=0, samples=0, channels, block_size;
	sscanf(argv[1], "%s", filename1);
	sscanf(argv[2], "%s", filename2);
	sscanf(argv[3], "%ld", &samples);
	sscanf(argv[4], "%ld", &block_size);
	sscanf(argv[5], "%ld", &channels);
	sscanf(argv[6], "%d", &inbits);
	sscanf(argv[7], "%d", &outbits);
	block_size=block_size*channels;
	float val1,val2,valw,valm,valm1;
	
	FILE *fptr;
	FILE *fptr1,*fptr2;
 
	fptr1=fopen(filename1,"rb");
	fptr2=fopen(filename2,"wb");

//  If inbits = 16 and outbits = 16
        if(inbits == 16 && outbits == 16)
        {
        float *bandpa;
        bandpa=(float *) calloc(channels, sizeof(float));
        uint16_t *ptr2;
        ptr2=(uint16_t *) calloc(block_size, sizeof(uint16_t));
        uint16_t *ptr1;
        ptr1 = (uint16_t *) calloc(block_size, sizeof(uint16_t));
        if(ptr1==NULL){
        printf("Could not allocate memory");}
        while(1==fread(ptr1,block_size*sizeof(uint16_t),1,fptr1))
        {
                printf(" processing bolck numbers %ld \n", k);
		memset(bandpa, 0, channels * sizeof(float));
                for(i=0;i<block_size;i++)
                {
                        j=i%channels;
                        val1=*(ptr1+i);
                        *(bandpa+j)=*(bandpa+j)+val1;
                }
                val1=block_size/channels;
                printf("samples %f \n",val1);
                for(i=0;i<channels;i++)
                {
                        *(bandpa+i)=*(bandpa+i)/val1;
                }
                printf("Done computing bandshape \n");
                uint16_t outtype_var;
                for(i==0;i<block_size;i++)
                {
                        val1=*(ptr1+i);
                        j=i%channels;
                        valw=(val1/(*(bandpa+j)))*120.0;
                        outtype_var=valw;
                        *(ptr2+i) = outtype_var;
                }
                fwrite(ptr2, sizeof(uint16_t), block_size, fptr2);
                printf("Wrote output to file \n");
                k=k+1;
        }
	free(bandpa);
	free(ptr2);
	free(ptr1);
        }  // Done case inbits=16, outbits=16

// If inbits = 8 and outbits = 8
        if(inbits == 8 && outbits == 8)
        {
        uint8_t *ptr1;
	float *bandpa;
	bandpa=(float *) calloc(channels, sizeof(float));
        ptr1 = (uint8_t *) calloc(block_size, sizeof(uint8_t));
	uint8_t *ptr2;
	ptr2=(uint8_t *) calloc(block_size, sizeof(uint8_t));
        if(ptr1==NULL){
        printf("Could not allocate memory");}

        while(1==fread(ptr1,block_size*sizeof(uint8_t),1,fptr1))
        {
                printf(" processing bolck numbers %ld \n", k);
		memset(bandpa, 0, channels * sizeof(float));
                for(i=0;i<block_size;i++)
                {
                        j=i%channels;
                        val1=*(ptr1+i);
                        *(bandpa+j)=*(bandpa+j)+val1;
                }
                val1=block_size/channels;
                printf("samples %f \n",val1);
                for(i=0;i<channels;i++)
                {
                        *(bandpa+i)=*(bandpa+i)/val1;
                }
                printf("Done computing bandshape \n");
                uint8_t outtype_var;
                for(i==0;i<block_size;i++)
                {
                        val1=*(ptr1+i);
                        j=i%channels;
                        valw=(val1/(*(bandpa+j)))*120.0;
                        outtype_var=valw;
                        *(ptr2+i) = outtype_var;
                }
                fwrite(ptr2, sizeof(uint8_t), block_size, fptr2);
                printf("Wrote output to file \n");
                k=k+1;
        }
	free(bandpa);
	free(ptr2);
	free(ptr1);
        }  // Done case inbits= 8 , outbits = 8

// If inbits = 16 and outbits = 8
	if(inbits == 16 && outbits == 8)
	{
	float *bandpa;
	bandpa=(float *) calloc(channels, sizeof(float));
        uint8_t *ptr2;
        ptr2=(uint8_t *) calloc(block_size, sizeof(uint8_t));
	uint16_t *ptr1;
	ptr1 = (uint16_t *) calloc(block_size, sizeof(uint16_t));
	if(ptr1==NULL){
	printf("Could not allocate memory");}
	
	while(1==fread(ptr1,block_size*sizeof(uint16_t),1,fptr1))
	{
		printf(" processing bolck numbers %ld \n", k);
		memset(bandpa, 0, channels * sizeof(float));
		for(i=0;i<block_size;i++)
		{
			j=i%channels;
			val1=*(ptr1+i);
			*(bandpa+j)=*(bandpa+j)+val1;
		}
		val1=block_size/channels;
		printf("samples %f \n",val1);
		for(i=0;i<channels;i++)
		{
			*(bandpa+i)=*(bandpa+i)/val1;
		}
		printf("Done computing bandshape \n");
		uint8_t outtype_var;
		for(i==0;i<block_size;i++)
		{
			val1=*(ptr1+i);
			j=i%channels;
			valw=(val1/(*(bandpa+j)))*120.0;
			outtype_var=valw;
			*(ptr2+i) = outtype_var;	
		}
		fwrite(ptr2, sizeof(uint8_t), block_size, fptr2);
		printf("Wrote output to file \n");
		k=k+1;
	}
	free(bandpa);
	free(ptr2);
	free(ptr1);
	}  // Done case inbits = 16 outbits = 8

	if(inbits == 8 && outbits == 16)
	{
	printf("Can not convert 8 bit input to 16 bit output\n");
	}
	
	rewind(fptr1);
	rewind(fptr2);
	fclose(fptr1);		
	fclose(fptr2);
}
