#!/bin/sh

### DocString ###
help_string="""
This script will use the umi tools docker to extract umis from reads
"""

### Arguments###
result_path=$1 # the to level results directory to be mounted; self.result_path
in1=$2 # trimmed read1 input
in2=$3 # trimmed read2 input
out1=$4 # umi extracted read1
out2=$5 # umi extracted read2

### Command ###
docker run \
    -v $result_path:/opt/result \
    quay.io/biocontainers/umi_tools:1.1.4--py38hbff2b2d_1 \
    umi_tools extract \
        --ignore-read-pair-suffixes \
        -I /opt/result/$in1 \
        --bc-pattern=NNNNNN \
        --read2-in=/opt/result/$in2 \
        --stdout=/opt/result/$out1 \
        --read2-out=/opt/result/$out2