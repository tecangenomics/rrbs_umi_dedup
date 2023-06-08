#!/bin/sh

help_string="""
This script will trim illumina adapter sequence
"""

### Arguments ###
pipeline_path=$1 # path to the trimRRBSdiversity... script to be MOUNTED; self.pipeline_path
result_path=$1 # the top level results folder that will be mounted; self.out_dir
read1=$2 # the read 1 to be trimmed; self.r1
read2=$3 # the read 2 to be trimmed; self.r2_new
### Command ###
docker run \
    -v $pipeline_path:/opt/pipeline
    -v $result_path:/opt/result \
    python:2.7.18-buster \
    /opt/pipeline/src/trimRRBSdiversityAdaptCustomers.py \
        -1 /opt/result/$read1 \
        -2 /opt/result/$read2