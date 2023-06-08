#!/bin/sh

help_string= """
This script will trim illumina adapter sequence
"""

### Arguments ###
reads_path=$1 # the raw reads folder to be mounted
result_path=$2 # the top level results folder that will be mounted
output_path=$3 # where
### Command ###
docker run \
    -v $reads_path:/opt/reads \
    -v $result_path:/opt/result \
    dukegcb/trim-galore:0.4.4 \
    trimgalore \
        -a AGATCGGAAGAGC \
        -a2 AGATCGGAAGAGC \
        --paired \
        -o /opt/result/$output \
        /opt/reads/$read1 \
        /opt/result/$read2