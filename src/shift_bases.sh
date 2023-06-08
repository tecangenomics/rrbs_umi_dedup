#!/bin/sh

### DocString ###
help_string= """
This script will use the python 3.12 docker to move bases (UMIs) from
one read to another read
"""

### Arguments###
pipeline_path=$1 # the directory of the pipeline to be mounted; self.pipeline_path
output_path=$2 # the to level results directory to be mounted; self.out_dir
reads_path=$3 # the raw reads directory to be mounted; self.read_dir
source=$4 # where to pull the UMIs from; includes path in results folder; self.r2
destination_new=$5 # where to store the UMIs; includes path in results folder; self.umi.fq
source_new=$6 # name of source file without UMIs; inludes path in results folder; self.r2_new

### Command ###
docker run \
    -v $pipeline_path:/opt/pipeline \
    -v $reads_path:/opt/reads \
    -v $output_path:/opt/result \
    python:3.12.0b1-bullseye \
    python /opt/pipeline/src/shift_bases.sh \
        -si /opt/reads/$source \
        -so /opt/result/$source_new \
        -do /opt/result/$destination_new