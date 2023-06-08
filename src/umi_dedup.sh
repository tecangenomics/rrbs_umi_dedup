#!/bin/sh

### DocString ###
help_string="""
This script will use the umi tools docker to extract umis from reads
"""

### Arguments###
result_path=$1 # the to level results directory to be mounted; self.result_path
output_dir=$2 # string of the result subdirectory
bam=$3 # bam file

### Command ###
docker run \
    -v $result_path:/opt/result \
    quay.io/biocontainers/umi_tools:1.1.4--py38hbff2b2d_1 \
    umi_tools dedup \
        -I /opt/result/$bam \
        --output_stats=/opt/result/$output_dir/${bam/.bam/dedup} \
        -S /opt/result/$output_dir/${bam/.bam/_dedup.bam}