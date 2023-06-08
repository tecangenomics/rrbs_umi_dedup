#!/bin/sh

help_string="""
This script will trim illumina adapter sequence
"""

### Arguments ###
reads_path=$1 # the raw reads folder to be mounted; self.read_path
result_path=$2 # the top level results folder that will be mounted; self.out_dir
output_path=$3 # where the output directory is for final reads; step_2_output
read1=$4 # the read 1 to be trimmed; self.r1
read2=$5 # the read 2 to be trimmed; self.r2_new
### Command ###
docker run \
    -v $reads_path:/opt/reads \
    -v $result_path:/opt/result \
    dukegcb/trim-galore:0.4.4 \
    trimgalore \
        -a AGATCGGAAGAGC \
        -a2 AGATCGGAAGAGC \
        --paired \
        -o /opt/result/$output_path \
        /opt/reads/$read1 \
        /opt/result/$read2