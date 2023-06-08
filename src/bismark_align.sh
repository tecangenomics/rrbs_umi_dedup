#!/bin/sh

### DocString ###
help_string= """
This script will use the bismark docker to do:
    alignment
"""

### Arguments###
result_path=$1 # the to level results directory to be mounted; self.result_path
genome_path=$2 # the path to the folder containing the indexed genome
output_path=$3 # the results subdirectory to save data to
in1=$4 # trimmed umi-extracted read1 input
in2=$5 # trimmed umi-extracted read2 input

### Command ###
docker run \
    -v $result_path:/opt/result \
    -v $genome_path:/opt/reference \
    quay.io/biocontainers/bismark:0.24.0--hdfd78af_0 \
    bismark \
        --genome $genome_path \
        --output_dir /opt/result/$output_path
        -1 /opt/result/$in1 \
        -2 /opt/result/$in2