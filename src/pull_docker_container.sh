#!/bin/sh

help_string= """
This script will pull all the docker containers needed
for the pipeline
"""

### Commands ###
# bismark 0.24.0
docker pull quay.io/biocontainers/bismark:0.24.0--hdfd78af_0

# python 2.7.18
docker pull python:2.7.18-buster

# python 3.12
docker pull python:3.12.0b1-bullseye

# trimgalore 0.4.4
docker pull dukegcb/trim-galore:0.4.4

# umi tools 1.1.4
docker pull quay.io/biocontainers/umi_tools:1.1.4--py38hbff2b2d_1