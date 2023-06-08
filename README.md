# rrbs_umi_dedup
Align RRBS reads and deduplicate from UMIs. The script will
call upon various docker files to run analysis--this should ensure that
this pipeline is as portable as possible.

# Requirements
Python 3.9 or higher \
Docker 

# Quickstart
To jump in start running the pipeline, use the command below \
```
python rrbs_umi_dedup/rrbs-aligner-mgi.py \
    -g /abs/path/to/genome/directory \
    -r /abs/path/to/reads/directory \
    -o /abs/path/to/results/directory \
    --index \
    --pull_docker
```

# How It Works
The pipeline will loop through reads in the given read directory and run scripts in the src directory. The scripts 
correspond to different steps in the pipeline using docker:\
1. Use https://github.com/tecangenomics/fq_base_shifter to move UMIs from read 2 (3' end) and move it to a temporary file.
2. Use trim_galore to trim universal adapters from read1 and the non-umi read2
3. Use a slightly modified version of https://github.com/tecangenomics/NuMetRRBS/tree/master (detailed in code header) to trim diversity adapters
4. Use https://github.com/tecangenomics/fq_base_shifter to move UMIs back to the trimmed read1 file (5' end)
5. Use umi_tools extract to extract UMIs from reads
6. Run bismark to align + sort bam file + index sorted bam file
7. Use umi_tools dedeup to deduplicate the sorted and indexed bam file

Outputs will be saved in different subdirectories within a provided output directory. The final deduplicated files
will be found in the subdirectory called "s6_deduplicate_bam"

# Parameters
**Required**
```
-g  The absolute path to the reference genome directory (not the file). \
-r  The absolute path to the reads directory. 
        Reads are assumed to be paired end.
        Reads must be in uncompressed format (fastq or fq, not fastq.gz or fq.gz).
        Read pairs are expected to be differentiated by R1 and R2.
        Read file names are expected to NOT have multiple instance of R1 or R2 in it.
-o  The absolute path to the output directory where the results will be stored
```
**Optional**
```
--index        Set this flag to index the reference genome with bismark
--pull_docker  Set this flag to pull the required docker images
```
# Additional Notes
Each step in the pipeline will be associated with a bash script that will call the docker command to execute what's needed.
If a different option is required for a particular step (e.g. changes in parallelization of alignment), please go to the
corresponding \*.sh file in the src directory and add those options.

Docker images called can also be found in a script in the src directory, change the docker pull command if a different version
of a software is preferred.

## How to install required software
### Python 3.9 or higher
You can install miniconda, a lightweight (version of anaconda) package manager that comes with python. An installation guide
can be found here: https://docs.conda.io/en/main/miniconda.html
### Docker
You can install docker with the commands below. The first 2 commands will install docker. The last 2 commands will make it such
that you don't have to run "sudo" everytime you run docker and that you don't need to restart the instance for that change
to take place.
```
sudo apt update
sudo apt install docker.io
sudo usermod -aGdocker $USER
newgrp docker
```
