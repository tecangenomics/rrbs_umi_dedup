#!/bin/sh

### DocString ###
help_string="""
This script will use the bismark docker to do:
    bam indexing
"""

### Arguments###
result_path=$1 # the to level results directory to be mounted; self.result_path
bam=$2 # bam file to index

### Command ###
docker run \
    -v $result_path:/opt/result \
    quay.io/biocontainers/bismark:0.24.0--hdfd78af_0 \
    samtools index /opt/result/$bam