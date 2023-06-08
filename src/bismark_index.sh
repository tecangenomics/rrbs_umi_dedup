#!/bin/sh

### DocString ###
help_string="""
This script will use the bismark docker container
and index the reference genome.
"""

### Arguments ###
genome_directory=$1


### Commands ###
#docker pull quay.io/biocontainers/bismark:0.24.0--hdfd78af_0

docker run \
    -v $genome_directory:/opt/reference \
    quay.io/biocontainers/bismark:0.24.0--hdfd78af_0 \
    bismark_genome_preparation /opt/reference